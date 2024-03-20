"""
    Patchexecutor handles the input and execution of the naoth lib
"""

import cppyy
import cppyy.ll
import os
import numpy as np
from cppyy_tools import get_naoth_dir, get_toolchain_dir, setup_shared_lib
from helper import Frame, load_image_as_yuv422
import PIL.Image
from PIL import PngImagePlugin
import ctypes
from pathlib import Path


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
        self.sim = cppyy.gbl.DummySimulator(False, 5401)
        cppyy.gbl.naoth.Platform.getInstance().init(self.sim)

        # create the cognition and motion objects
        cog = cppyy.gbl.createCognition()
        mo = cppyy.gbl.createMotion()

        # cast to callable
        callable_cog = cppyy.bind_object(
            cppyy.addressof(cog), cppyy.gbl.naoth.Callable)
        callable_mo = cppyy.bind_object(
            cppyy.addressof(mo), cppyy.gbl.naoth.Callable)

        self.sim.registerCognition(callable_cog)
        self.sim.registerMotion(callable_mo)
        
        # get access to the module manager and return it to the calling function
        self.moduleManager = cppyy.gbl.getModuleManager(cog)
        
        # get the ball detector module
        self.ball_detector = self.moduleManager.getModule("CNNBallDetector").getModule()
        
        # disable the modules providing the camera matrix, because we want to use our own
        self.moduleManager.getModule("CameraMatrixFinder").setEnabled(False)
        self.moduleManager.getModule("FakeCameraMatrixFinder").setEnabled(False)
        
        cppyy.cppdef("""
               Pose3D* toPose3D(CameraMatrix* m) { return static_cast<Pose3D*>(m); }
                """)
        
        # restore original working directory
        os.chdir(orig_working_dir)

    def convert_image_to_frame(self, image_path):
        img = PIL.Image.open(image_path)

        bottom = img.info["CameraID"] == "1"
        # parse camera matrix using metadata in the PNG file
        cam_matrix_translation = (float(img.info["t_x"]), float(
            img.info["t_y"]), float(img.info["t_z"]))

        cam_matrix_rotation = np.array(
            [
                [float(img.info["r_11"]), float(
                    img.info["r_12"]), float(img.info["r_13"])],
                [float(img.info["r_21"]), float(
                    img.info["r_22"]), float(img.info["r_23"])],
                [float(img.info["r_31"]), float(
                    img.info["r_32"]), float(img.info["r_33"])]
            ])
        
        # HACK - we need to figure out a good way to handle groundtruth also not just for balls
        gt_balls = []

        return Frame(image_path, bottom, gt_balls, cam_matrix_translation, cam_matrix_rotation)


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

    def set_current_frame(self, frame):

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
        for p in detected_balls.patchesYUVClassified:
            cv2.rectangle(img, (p.min.x, p.min.y), (p.max.x, p.max.y), (0, 0, 255))

        # draw groundtruth
        for gt_ball in frame.gt_balls:
            cv2.rectangle(img, gt_ball.top_left, gt_ball.bottom_right, (0, 255, 0))
            Path(frame.file).stem + f"_debug.png"
        print(Path(frame.file).stem + f"_debug.png")
        output_file = Path(frame.file).stem + f"_debug.png"
        #Path(output_file.parent).mkdir(exist_ok=True, parents=True)
        cv2.imwrite(str(output_file), img)

    def export_patches(self, frame: Frame):
        """
            This function exports patches as images for future training. All interesting meta information is saved inside the png header
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
        # create folder for the patches

        patch_folder = "patch_output"
        Path(patch_folder).mkdir(exist_ok=True, parents=True)

        for idx, p in enumerate(detected_balls.patchesYUVClassified):
            iou = 0.0
            x = 0.0
            y = 0.0
            radius = 0.0
            # calculate the best iou for a given patch
            for gt_ball in frame.gt_balls:
                new_iou = gt_ball.intersection_over_union(p.min.x, p.min.y, p.max.x, p.max.y)
                if new_iou > iou:
                    iou = new_iou
                    # those values are relativ to the origin (top left) of the patch 
                    x, y = gt_ball.get_center()
                    x = x - p.min.x
                    y = y - p.min.y
                    radius = gt_ball.get_radius()


            # crop full image to calculated patch
            # TODO use naoth like resizing (subsampling) like in Patchwork.cpp line 39
            crop_img = img[p.min.y:p.max.y, p.min.x:p.max.x]
            #print(f"size: {crop_img.size}")
            #if crop_img.empt:
            #    print(f"\timage with index {idx} was empty")
            #    continue
            # don't resize here. do it later
            #crop_img = cv2.resize(crop_img, (patch_size, patch_size), interpolation=cv2.INTER_NEAREST)

            # FIXME: here we save the image with opencv and then open it again with pil to add meta data
            # can we do that without saving twice?
            patch_file_name = Path(patch_folder) / (Path(frame.file).stem + f"_{idx}.png")
            cv2.imwrite(str(patch_file_name), crop_img)

            # section for writing meta data
            meta = PngImagePlugin.PngInfo()
            meta.add_text("CameraID", str(cam_id))
            meta.add_text("iou", str(iou))
            meta.add_text("center_x", str(x))
            meta.add_text("center_y", str(y))
            meta.add_text("radius", str(radius))

            with PIL.Image.open(str(patch_file_name)) as im_pill:
                im_pill.save(str(patch_file_name), pnginfo=meta)
        
        return Path(patch_folder).resolve()
