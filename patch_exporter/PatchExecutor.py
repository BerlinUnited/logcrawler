"""
    Patchexecutor handles the input and execution of the naoth lib
"""

import ctypes
import os
from pathlib import Path
from typing import Dict, List, Union

import cppyy
import cppyy.ll
import numpy as np
import PIL.Image
from cppyy_tools import get_naoth_dir, get_toolchain_dir, setup_shared_lib
from helper import BoundingBox, Frame, load_image_as_yuv422, load_image_as_yuv422_y_only_better
from PIL import PngImagePlugin
import tensorflow as tf


class PatchExecutor:
    """
    TODO add documentation here
    """

    def __init__(self):
        orig_working_dir = os.getcwd()

        setup_shared_lib(get_naoth_dir(), get_toolchain_dir())

        # change working directory so that the configuration is found
        os.chdir(os.path.join(get_naoth_dir(), "NaoTHSoccer"))
        print(os.getcwd())

        # start dummy simulator
        cppyy.gbl.g_type_init()
        self.sim = cppyy.gbl.DummySimulator(True, 5401)
        cppyy.gbl.naoth.Platform.getInstance().init(self.sim)
        # create the cognition and motion objects
        cog = cppyy.gbl.createCognition()
        mo = cppyy.gbl.createMotion()

        # cast to callable
        callable_cog = cppyy.bind_object(cppyy.addressof(cog), cppyy.gbl.naoth.Callable)
        callable_mo = cppyy.bind_object(cppyy.addressof(mo), cppyy.gbl.naoth.Callable)

        self.sim.registerCognition(callable_cog)
        self.sim.registerMotion(callable_mo)

        # get access to the module manager and return it to the calling function
        self.moduleManager = cppyy.gbl.getModuleManager(cog)

        # get the ball detector module
        self.ball_detector = self.moduleManager.getModule("CNNBallDetector").getModule()

        # disable the modules providing the camera matrix, because we want to use our own
        self.moduleManager.getModule("CameraMatrixFinder").setEnabled(False)
        self.moduleManager.getModule("FakeCameraMatrixFinder").setEnabled(False)

        cppyy.cppdef(
            """
               Pose3D* toPose3D(CameraMatrix* m) { return static_cast<Pose3D*>(m); }
                """
        )
        # restore original working directory
        os.chdir(orig_working_dir)

    def convert_image_to_frame(
        self,
        image_path,
        gt_balls=None,
        gt_robots=None,
        gt_penalties=None,
    ):
        gt_balls = gt_balls or []
        gt_robots = gt_robots or []
        gt_penalties = gt_penalties or []

        # HACK - we need to figure out a good way to handle groundtruth also not just for balls
        img = PIL.Image.open(image_path)

        bottom = img.info["CameraID"] == "1"
        # parse camera matrix using metadata in the PNG file
        cam_matrix_translation = (
            float(img.info["t_x"]),
            float(img.info["t_y"]),
            float(img.info["t_z"]),
        )

        cam_matrix_rotation = np.array(
            [
                [
                    float(img.info["r_11"]),
                    float(img.info["r_12"]),
                    float(img.info["r_13"]),
                ],
                [
                    float(img.info["r_21"]),
                    float(img.info["r_22"]),
                    float(img.info["r_23"]),
                ],
                [
                    float(img.info["r_31"]),
                    float(img.info["r_32"]),
                    float(img.info["r_33"]),
                ],
            ]
        )

        return Frame(
            file=image_path,
            bottom=bottom,
            cam_matrix_translation=cam_matrix_translation,
            cam_matrix_rotation=cam_matrix_rotation,
            gt_balls=gt_balls,
            gt_robots=gt_robots,
            gt_penalties=gt_penalties,
        )

    @staticmethod
    def set_camera_matrix_representation(frame, cam_matrix):
        """
        reads the camera matrix information from a frame object and writes it to the
        naoth camMatrix representation
        """
        p = cppyy.gbl.toPose3D(cam_matrix)
        p.translation.x = frame.cam_matrix_translation[0]
        p.translation.y = frame.cam_matrix_translation[1]
        p.translation.z = frame.cam_matrix_translation[2]

        for c in range(0, 3):
            for r in range(0, 3):
                p.rotation.c[c][r] = frame.cam_matrix_rotation[r, c]

        return p

    # helper: write a numpy array of data to an image representation
    @staticmethod
    def write_data_to_image_representation(data, image):
        # create a pointer
        p_data = data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))

        # move image data into the Image representation that is defined in the Commons C++ project
        # the copyImageDataYUV422 function is defined there
        image.copyImageDataYUV422(p_data, data.size)

    def set_current_frame(self, frame: Frame):

        # get access to relevant representations
        image_bottom = self.ball_detector.getRequire().at("Image")
        image_top = self.ball_detector.getRequire().at("ImageTop")
        cam_matrix_bottom = self.ball_detector.getRequire().at("CameraMatrix")
        cam_matrix_top = self.ball_detector.getRequire().at("CameraMatrixTop")

        cam_matrix_bottom.valid = False
        cam_matrix_top.valid = False

        # load image in YUV422 format
        yuv422 = load_image_as_yuv422(frame.file)
        black = np.zeros(640 * 480 * 2, np.uint8)

        """
        get reference to the image input representation, if the current image is from the bottom camera
        we set the image for bottom image and the top image to black
        """
        if frame.bottom:
            self.write_data_to_image_representation(yuv422, image_bottom)
            self.write_data_to_image_representation(black, image_top)

            self.set_camera_matrix_representation(frame, cam_matrix_bottom)
            cam_matrix_bottom.valid = True
        else:  # image is from top camera
            self.write_data_to_image_representation(black, image_bottom)
            self.write_data_to_image_representation(yuv422, image_top)

            self.set_camera_matrix_representation(frame, cam_matrix_top)
            cam_matrix_bottom.valid = False

    def get_best_ball_overlap(self, patch, gt_balls: List[BoundingBox]):
        # find the ground truth ball with the highest intersection ratio
        # with the current patch, ie. the ball that is most contained in the patch.
        # This also returns the center and radius of the ball in the patch coordinate system

        x, y, radius, gt_ball_intersect_ratio = 0.0, 0.0, 0.0, 0.0
        if isinstance(patch, BoundingBox):
            patch_box = patch
        else:
            patch_box = BoundingBox.from_coords(
                patch.min.x, patch.min.y, patch.max.x, patch.max.y
            )

        for gt_ball in gt_balls:

            intersection = gt_ball.intersection(patch_box)

            if intersection is None:
                continue

            # we are interested in the percentage of the ground truth balls area
            # which is contained inside the current patch
            new_gt_ball_intersect_ratio = intersection.area / gt_ball.area

            if new_gt_ball_intersect_ratio > gt_ball_intersect_ratio:
                gt_ball_intersect_ratio = new_gt_ball_intersect_ratio

                # those values are relativ to the origin (top left) of the patch
                x = gt_ball.center[0] - patch_box.top_left.x
                y = gt_ball.center[1] - patch_box.top_left.y
                radius = gt_ball.radius

        return x, y, radius, gt_ball_intersect_ratio

    def get_best_overlap(
        self,
        patch,
        gt_objects: List[BoundingBox],
        intersect_denominator: str = "gt",
    ):
        # find the ground object with the highest intersection ratio

        if intersect_denominator not in ("gt", "patch"):
            raise ValueError(
                f"intersect_denominator must be 'gt' or 'patch', but is {intersect_denominator}"
            )

        x, y, intersect_ratio = 0.0, 0.0, 0.0

        if isinstance(patch, BoundingBox):
            patch_box = patch
        else:
            patch_box = BoundingBox.from_coords(
                patch.min.x, patch.min.y, patch.max.x, patch.max.y
            )

        for gt_box in gt_objects:
            intersection = gt_box.intersection(patch_box)

            if intersection is None:
                continue

            # when intersect_denominator is 'gt', we are interested in the percentage
            # of the ground truth area which is contained inside the intersection
            #
            # when intersect_denominator is 'patch', we are interested in the percentage
            # of the patch area which is contained inside the intersection. This is
            # useful for robot bboxes which are often significantly larger than the patch
            denominator = (
                gt_box.area if intersect_denominator == "gt" else patch_box.area
            )

            new_intersect_ratio = intersection.area / denominator

            if new_intersect_ratio > intersect_ratio:
                intersect_ratio = new_intersect_ratio

                # those values are relativ to the origin (top left) of the patch
                x = gt_box.center[0] - patch_box.top_left.x
                y = gt_box.center[1] - patch_box.top_left.y

        return x, y, intersect_ratio

    def export_debug_images(self, frame: Frame):
        """
        this function exports the input images with the calculated patches overlayed
        """
        import cv2

        # get the ball candidates from the module
        if frame.bottom:
            detected_balls = self.ball_detector.getProvide().at("BallCandidates")
        else:
            detected_balls = self.ball_detector.getProvide().at("BallCandidatesTop")

        img = cv2.imread(frame.file)

        # draw patches
        for patch in detected_balls.patchesYUVClassified:
            cv2.rectangle(
                img,
                pt1=(patch.min.x, patch.min.y),
                pt2=(patch.max.x, patch.max.y),
                color=(0, 0, 255),
            )

        # draw groundtruth
        for gt_ball in frame.gt_balls:
            cv2.rectangle(
                img,
                pt1=gt_ball.top_left.as_cv2_point(),
                pt2=gt_ball.bottom_right.as_cv2_point(),
                color=(0, 255, 0),
            )
            cv2.circle(
                img,
                center=gt_ball.center,
                radius=gt_ball.radius,
                color=(255, 0, 0),
            )

        output_file = Path(frame.file).parent / (Path(frame.file).stem + "_debug.png")
        cv2.imwrite(str(output_file), img)

    def write_patch_to_file(
        self,
        patch: np.ndarray,
        frame: Frame,
        bucketname: str,
        output_folder: Path,
        idx: int,
        intersect: Union[float, str],
        meta_info: Dict,
    ):
        import cv2

        if isinstance(intersect, float):
            intersect = f"{intersect:.4f}"

        patch_file_name = Path(output_folder) / (
            bucketname
            + "_"
            + Path(frame.file).stem
            + f"_{idx}_intersect_{intersect}.png"
        )

        # write patch to file
        try:
            # opencv does not support writing png meta data,
            # so we have to use PIL for that
            cv2.imwrite(str(patch_file_name), patch)
        except Exception as e:
            print(f"\nError writing file with cv2: {e}")
            print(f"file: {frame.file}")
            print(f"size: {patch.size}")
        else:
            # image was written successfully, now add the meta data with PIL
            meta = PngImagePlugin.PngInfo()

            for key, value in meta_info.items():
                meta.add_text(key, str(value))

            with PIL.Image.open(str(patch_file_name)) as im_pil:
                im_pil.save(str(patch_file_name), pnginfo=meta)


    def export_patches(
        self,
        frame: Frame,
        output_patch_folder: Path,
        bucketname: str,
        min_gt_intersect_ratio: float = 0.2,
        debug: bool = False,
    ):
        """
        This function exports patches as images for future training.
        All relvant meta information is saved inside the png header
        """
        import cv2

        # get the ball candidates from the module
        if frame.bottom:
            detected_balls = self.ball_detector.getProvide().at("BallCandidates")
            cam_id = 1
        else:
            detected_balls = self.ball_detector.getProvide().at("BallCandidatesTop")
            cam_id = 0

        img = cv2.imread(frame.file)

        ball_folder = output_patch_folder / "ball"
        robot_folder = output_patch_folder / "robot"
        penalty_folder = output_patch_folder / "penalty"
        other_folder = output_patch_folder / "other"

        Path(ball_folder).mkdir(exist_ok=True, parents=True)
        Path(robot_folder).mkdir(exist_ok=True, parents=True)
        Path(penalty_folder).mkdir(exist_ok=True, parents=True)
        Path(other_folder).mkdir(exist_ok=True, parents=True)

        for idx, patch in enumerate(detected_balls.patchesYUVClassified):
            # TODO use naoth like resizing (subsampling) like in Patchwork.cpp line 39
            # crop full image to calculated patch
            crop_img = img[patch.min.y : patch.max.y, patch.min.x : patch.max.x]

            # compute overlaps with ground truth bounding boxes for
            # ball, robot and penalty mark

            # get percentage of ball area that is contained in intersection
            ball_x, ball_y, ball_radius, gt_ball_intersect_ratio = (
                self.get_best_ball_overlap(patch, frame.gt_balls)
            )

            # get percentage of penalty mark area that is contained in intersection
            penalty_x, penalty_y, gt_penalty_intersect_ratio = self.get_best_overlap(
                patch, frame.gt_penalties, intersect_denominator="gt"
            )

            # get percentage of PATCH are that is contained in intersection
            robot_x, robot_y, gt_robot_intersect_ratio = self.get_best_overlap(
                patch, frame.gt_robots, intersect_denominator="patch"
            )

            meta_info = {
                "CameraID": cam_id,
                "ball_intersect": gt_ball_intersect_ratio,
                "penalty_intersect": gt_penalty_intersect_ratio,
                "robot_intersect": gt_robot_intersect_ratio,
                "ball_center_x": ball_x,
                "ball_center_y": ball_y,
                "ball_radius": ball_radius,
                "penalty_center_x": penalty_x,
                "penalty_center_y": penalty_y,
                "robot_center_x": robot_x,
                "robot_center_y": robot_y,
                "p_min_x": patch.min.x,
                "p_min_y": patch.min.y,
                "p_max_x": patch.max.y,
                "p_max_y": patch.max.x
            }

            # Here we perform a hierarchical decision on the patch class.
            # precedence: ball > penalty > robot > non-ball
            # That means a patch can only belong to one class, for multiclass
            # applications one needs to parse the meta information of all png files

            # if the patch contains a ball, write it to the ball folder
            if gt_ball_intersect_ratio > min_gt_intersect_ratio:
                if debug:
                    cv2.circle(
                        crop_img,
                        center=(int(ball_x), int(ball_y)),
                        radius=int(ball_radius),
                        color=(255, 0, 0),
                        thickness=2,
                    )

                self.write_patch_to_file(
                    crop_img,
                    frame,
                    bucketname,
                    ball_folder,
                    idx,
                    gt_ball_intersect_ratio,
                    meta_info,
                )

            # if the patch contains a penalty mark and no ball,
            # write it to the penalty folder
            elif gt_penalty_intersect_ratio > min_gt_intersect_ratio:
                self.write_patch_to_file(
                    crop_img,
                    frame,
                    bucketname,
                    penalty_folder,
                    idx,
                    gt_penalty_intersect_ratio,
                    meta_info,
                )

            # if the patch contains a robot and no ball or penalty mark,
            # write it to the robot folder
            elif gt_robot_intersect_ratio > min_gt_intersect_ratio:
                self.write_patch_to_file(
                    crop_img,
                    frame,
                    bucketname,
                    robot_folder,
                    idx,
                    gt_robot_intersect_ratio,
                    meta_info,
                )

            # if the patch contains none of the above, write it to the other folder
            else:
                # we write out all intersection values for debugging purposes
                intersect = (
                    f"ball_inter_{gt_ball_intersect_ratio:.4f}_"
                    f"penalty_inter_{gt_penalty_intersect_ratio:.4f}_"
                    f"robot_inter_{gt_robot_intersect_ratio:.4f}"
                )
                self.write_patch_to_file(
                    crop_img, frame, bucketname, other_folder, idx, intersect, meta_info
                )


    def export_patches_segmentation(
        self,
        frame: Frame,
        output_patch_folder: Path,
        bucketname: str,
        min_gt_intersect_ratio: float = 0.2,
        debug: bool = False,
        model=None,
        extra_border = 0
    ):
        """
        This function exports patches as images for future training.
        All relvant meta information is saved inside the png header
        """
        import cv2

        # get the ball candidates from the module
        patch_list_segmentation = list()
        if frame.bottom:
            cam_id = 1
            input_image = load_image_as_yuv422_y_only_better(frame.file)
            image_input = np.expand_dims(input_image, axis=0)
            result = model.predict(image_input, verbose = 0)
            result = result[0]
            ball_result = result[:,:,0]
            factor = 32
            upscaled_array = np.repeat(np.repeat(ball_result, factor, axis=0), factor, axis=1)
            threshold_value = 0.5
            binary_mask = np.uint8(upscaled_array > threshold_value) * 255
            if sum == 0:
                return
            # Find contours
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for idx, contour in enumerate(contours):
                x, y, w, h = cv2.boundingRect(contour)
                patch_box = BoundingBox.from_coords(
                    x, y, x+w, y+h
                )
                patch_list_segmentation.append(patch_box)
        else:
            return

        img = cv2.imread(frame.file)

        ball_folder = output_patch_folder / "ball"
        robot_folder = output_patch_folder / "robot"
        penalty_folder = output_patch_folder / "penalty"
        other_folder = output_patch_folder / "other"

        Path(ball_folder).mkdir(exist_ok=True, parents=True)
        Path(robot_folder).mkdir(exist_ok=True, parents=True)
        Path(penalty_folder).mkdir(exist_ok=True, parents=True)
        Path(other_folder).mkdir(exist_ok=True, parents=True)

        for idx, patch in enumerate(patch_list_segmentation):
            # calculate extra space around the found patch if possible
            top_left_y = patch.top_left.y - extra_border if patch.top_left.y - extra_border > 0 else patch.top_left.y
            bottom_right_y = patch.bottom_right.y - extra_border if patch.bottom_right.y + extra_border > img.shape[0] else patch.bottom_right.y
            top_left_x = patch.top_left.x - extra_border if patch.top_left.x - extra_border > 0 else patch.top_left.x
            bottom_right_x = patch.bottom_right.x - extra_border if patch.bottom_right.x + extra_border > img.shape[1] else patch.bottom_right.x

            # TODO use naoth like resizing (subsampling) like in Patchwork.cpp line 39
            # crop full image to calculated patch
            crop_img = img[top_left_y : bottom_right_y, top_left_x : bottom_right_x]

            # compute overlaps with ground truth bounding boxes for
            # ball, robot and penalty mark

            # get percentage of ball area that is contained in intersection
            ball_x, ball_y, ball_radius, gt_ball_intersect_ratio = (
                self.get_best_ball_overlap(patch, frame.gt_balls)
            )

            # get percentage of penalty mark area that is contained in intersection
            penalty_x, penalty_y, gt_penalty_intersect_ratio = self.get_best_overlap(
                patch, frame.gt_penalties, intersect_denominator="gt"
            )

            # get percentage of PATCH are that is contained in intersection
            robot_x, robot_y, gt_robot_intersect_ratio = self.get_best_overlap(
                patch, frame.gt_robots, intersect_denominator="patch"
            )

            meta_info = {
                "CameraID": cam_id,
                "ball_intersect": gt_ball_intersect_ratio,
                "penalty_intersect": gt_penalty_intersect_ratio,
                "robot_intersect": gt_robot_intersect_ratio,
                "ball_center_x": ball_x,
                "ball_center_y": ball_y,
                "ball_radius": ball_radius,
                "penalty_center_x": penalty_x,
                "penalty_center_y": penalty_y,
                "robot_center_x": robot_x,
                "robot_center_y": robot_y,
                "p_min_x": patch.top_left.x,
                "p_min_y": patch.top_left.y,
                "p_max_x": patch.bottom_right.x,
                "p_max_y": patch.bottom_right.y
            }

            # Here we perform a hierarchical decision on the patch class.
            # precedence: ball > penalty > robot > non-ball
            # That means a patch can only belong to one class, for multiclass
            # applications one needs to parse the meta information of all png files

            # if the patch contains a ball, write it to the ball folder
            if gt_ball_intersect_ratio > min_gt_intersect_ratio:
                if debug:
                    cv2.circle(
                        crop_img,
                        center=(int(ball_x), int(ball_y)),
                        radius=int(ball_radius),
                        color=(255, 0, 0),
                        thickness=2,
                    )

                self.write_patch_to_file(
                    crop_img,
                    frame,
                    bucketname,
                    ball_folder,
                    idx,
                    gt_ball_intersect_ratio,
                    meta_info,
                )

            # if the patch contains a penalty mark and no ball,
            # write it to the penalty folder
            elif gt_penalty_intersect_ratio > min_gt_intersect_ratio:
                self.write_patch_to_file(
                    crop_img,
                    frame,
                    bucketname,
                    penalty_folder,
                    idx,
                    gt_penalty_intersect_ratio,
                    meta_info,
                )

            # if the patch contains a robot and no ball or penalty mark,
            # write it to the robot folder
            elif gt_robot_intersect_ratio > min_gt_intersect_ratio:
                self.write_patch_to_file(
                    crop_img,
                    frame,
                    bucketname,
                    robot_folder,
                    idx,
                    gt_robot_intersect_ratio,
                    meta_info,
                )

            # if the patch contains none of the above, write it to the other folder
            else:
                # we write out all intersection values for debugging purposes
                intersect = (
                    f"ball_inter_{gt_ball_intersect_ratio:.4f}_"
                    f"penalty_inter_{gt_penalty_intersect_ratio:.4f}_"
                    f"robot_inter_{gt_robot_intersect_ratio:.4f}"
                )
                self.write_patch_to_file(
                    crop_img, frame, bucketname, other_folder, idx, intersect, meta_info
                )
