from naoth.log import Reader as LogReader
from naoth.log import Parser
from pathlib import Path
from tqdm import tqdm
import numpy as np
import io
from PIL import PngImagePlugin
from PIL import Image as PIL_Image


def export_images(
    logfile_path,
    data,
    output_folder_top,
    output_folder_bottom,
    out_top_jpg,
    out_bottom_jpg,
):
    """
    creates two folders:
        <logfile name>_top
        <logfile name>_bottom

    and saves the images inside those folders
    """

    i, img_b, img_b_jpg, img_t, img_t_jpg, cm_b, cm_t = data
    frame_number = format(
        i, "07d"
    )  # make frame number a fixed length string so that the images are in the correct order
    if img_b:
        img_b = img_b.convert("RGB")
        save_image_to_png(
            frame_number, img_b, cm_b, output_folder_bottom, cam_id=1, name=logfile_path
        )
    # TODO add meta data indicating this was a jpeg image
    if img_b_jpg:
        img_b_jpg = img_b_jpg.convert("RGB")
        save_image_to_png(
            frame_number, img_b_jpg, cm_b, out_bottom_jpg, cam_id=1, name=logfile_path
        )

    if img_t:
        img_t = img_t.convert("RGB")
        save_image_to_png(
            frame_number, img_t, cm_t, output_folder_top, cam_id=0, name=logfile_path
        )

    # TODO add meta data indicating this was a jpeg image
    if img_t_jpg:
        img_t_jpg = img_t_jpg.convert("RGB")
        save_image_to_png(
            frame_number, img_t_jpg, cm_t, out_top_jpg, cam_id=0, name=logfile_path
        )


def get_images(frame):
    try:
        image_top = image_from_proto(frame["ImageTop"])
    except KeyError:
        image_top = None

    try:
        image_top_jpeg = image_from_proto_jpeg(frame["ImageJPEGTop"])
    except KeyError:
        image_top_jpeg = None

    try:
        cm_top = frame["CameraMatrixTop"]
    except KeyError:
        cm_top = None

    try:
        image_bottom = image_from_proto(frame["Image"])
    except KeyError:
        image_bottom = None

    try:
        image_bottom_jpeg = image_from_proto_jpeg(frame["ImageJPEG"])
    except KeyError:
        image_bottom_jpeg = None

    try:
        cm_bottom = frame["CameraMatrix"]
    except KeyError:
        cm_bottom = None

    return (
        frame.number,
        image_bottom,
        image_bottom_jpeg,
        image_top,
        image_top_jpeg,
        cm_bottom,
        cm_top,
    )


def image_from_proto(message):
    # read each channel of yuv422 separately
    yuv422 = np.frombuffer(message.data, dtype=np.uint8)
    y = yuv422[0::2]
    u = yuv422[1::4]
    v = yuv422[3::4]

    # convert from yuv422 to yuv888
    yuv888 = np.zeros(message.height * message.width * 3, dtype=np.uint8)

    yuv888[0::3] = y
    yuv888[1::6] = u
    yuv888[2::6] = v
    yuv888[4::6] = u
    yuv888[5::6] = v

    yuv888 = yuv888.reshape((message.height, message.width, 3))

    # convert the image to rgb and save it
    img = PIL_Image.frombytes(
        "YCbCr", (message.width, message.height), yuv888.tobytes()
    )
    return img


def image_from_proto_jpeg(message):
    # hack:
    if message.format == message.JPEG:
        # unpack JPG
        img = PIL_Image.open(io.BytesIO(message.data))

        # HACK: for some reason the decoded image is inverted ...
        yuv422 = 255 - np.array(img, dtype=np.uint8)

        # flatten the image to get the same data formal like a usual yuv422
        yuv422 = yuv422.reshape(message.height * message.width * 2)
    else:
        # read each channel of yuv422 separately
        yuv422 = np.frombuffer(message.data, dtype=np.uint8)

    y = yuv422[0::2]
    u = yuv422[1::4]
    v = yuv422[3::4]

    # convert from yuv422 to yuv888
    yuv888 = np.zeros(message.height * message.width * 3, dtype=np.uint8)

    yuv888[0::3] = y
    yuv888[1::6] = u
    yuv888[2::6] = v
    yuv888[4::6] = u
    yuv888[5::6] = v

    yuv888 = yuv888.reshape((message.height, message.width, 3))

    # convert the image to rgb
    img = PIL_Image.frombytes(
        "YCbCr", (message.width, message.height), yuv888.tobytes()
    )

    return img


def save_image_to_png(j, img, cm, target_dir, cam_id, name):
    meta = PngImagePlugin.PngInfo()
    meta.add_text("Message", "rotation maxtrix is saved column wise")
    meta.add_text("logfile", str(name))
    meta.add_text("CameraID", str(cam_id))

    if cm:
        meta.add_text("t_x", str(cm.pose.translation.x))
        meta.add_text("t_y", str(cm.pose.translation.y))
        meta.add_text("t_z", str(cm.pose.translation.z))

        meta.add_text("r_11", str(cm.pose.rotation[0].x))
        meta.add_text("r_21", str(cm.pose.rotation[0].y))
        meta.add_text("r_31", str(cm.pose.rotation[0].z))

        meta.add_text("r_12", str(cm.pose.rotation[1].x))
        meta.add_text("r_22", str(cm.pose.rotation[1].y))
        meta.add_text("r_32", str(cm.pose.rotation[1].z))

        meta.add_text("r_13", str(cm.pose.rotation[2].x))
        meta.add_text("r_23", str(cm.pose.rotation[2].y))
        meta.add_text("r_33", str(cm.pose.rotation[2].z))
    filename = Path(target_dir) / (str(j) + ".png")
    img.save(filename, pnginfo=meta)


if __name__ == "__main__":
    log_path = "/mnt/d/logs/2024-07-15_RC24/2024-07-15_20-00-00_BerlinUnited_vs_SPQR_half1-test/game_logs/2_16_Nao0017_240715-1830/combined.log"
    out_top = "out_top"
    out_bottom = "out_bottom"
    out_top_jpg = "out_top_jpg"
    out_bottom_jpg = "out_bottom_jpg"

    Path(out_top).mkdir(exist_ok=True, parents=True)
    Path(out_bottom).mkdir(exist_ok=True, parents=True)
    Path(out_top_jpg).mkdir(exist_ok=True, parents=True)
    Path(out_bottom_jpg).mkdir(exist_ok=True, parents=True)

    my_parser = Parser()
    my_parser.register("ImageJPEG", "Image")
    my_parser.register("ImageJPEGTop", "Image")
    game_log = LogReader(str(log_path), my_parser)

    for idx, frame in enumerate(tqdm(game_log)):
        try:
            frame_number = frame["FrameInfo"].frameNumber
            frame_time = frame["FrameInfo"].time
        except Exception as e:
            print(
                "FrameInfo not found in current frame - will not parse any other frames from this log and continue with the next one"
            )
            print(e)
            break

        data = get_images(frame)
        export_images(
            log_path,
            data,
            str(out_top),
            str(out_bottom),
            str(out_top_jpg),
            str(out_bottom_jpg),
        )

    # HACK delete image folders if they are empty - this is just so that looking at the extracted folder is not confusing for humans
    if not any(out_top_jpg.iterdir()):
        out_top_jpg.rmdir()
    if not any(out_bottom_jpg.iterdir()):
        out_bottom_jpg.rmdir()
    if not any(out_top.iterdir()):
        out_top.rmdir()
    if not any(out_bottom.iterdir()):
        out_bottom.rmdir()
