"""
    Image Extractor
"""
from pathlib import Path
import numpy as np
from PIL import PngImagePlugin
import shutil
from PIL import Image as PIL_Image
from naoth.log import Reader as LogReader
from naoth.log import Parser
import sys



def export_images(logfile, img):
    """
        creates two folders:
            <logfile name>_top
            <logfile name>_bottom

        and saves the images inside those folders
    """
    # TODO naming is weird logfile_name is not really what it says it is
    extracted_folder = Path(logfile).parent.parent.parent / Path("extracted") / Path(logfile).parent.name
    logfile_name = extracted_folder / Path(logfile).stem
    output_folder_top = Path(str(logfile_name) + "_top")
    output_folder_bottom = Path(str(logfile_name) + "_bottom")

    output_folder_top.mkdir(exist_ok=True, parents=True)
    output_folder_bottom.mkdir(exist_ok=True, parents=True)
    
    # the order changed in 2023
    # TODO add the code from max here
    for i, img_b, img_t, cm_b, cm_t in img:
        if img_b:
            img_b = img_b.convert('RGB')
            save_image_to_png(i, img_b, cm_b, output_folder_bottom, cam_id=1, name=logfile)

        if img_t:
            img_t = img_t.convert('RGB')
            save_image_to_png(i, img_t, cm_t, output_folder_top, cam_id=0, name=logfile)

        print("saving images from frame ", i)

    # zip the images
    # FIXME: it does not zip the correct thing
    """
    output_zipfile_top = Path(output_folder_top)
    if output_zipfile_top.is_file():
        print("\tframes.zip file already exists. Will continue with the next game")
    else:
        shutil.make_archive(str(output_zipfile_top), format="zip")
        # remove the extracted images after zipping
        shutil.rmtree(output_folder_top)

    output_zipfile_bottom = Path(output_folder_bottom)
    if output_zipfile_bottom.is_file():
        print("\tframes.zip file already exists. Will continue with the next game")
    else:
        shutil.make_archive(str(output_zipfile_bottom), format="zip")
        # remove the extracted images after zipping
        shutil.rmtree(output_folder_bottom)

    # TODO maybe its better to have the images not zipped for later
    """

def get_images(frame):
    try:
        image_top = image_from_proto(frame["ImageTop"])
    except KeyError:
        image_top = None

    try:
        cm_top = frame["CameraMatrixTop"]
    except KeyError:
        cm_top = None

    try:
        image_bottom = image_from_proto(frame["Image"])
    except KeyError:
        image_bottom = None

    try:
        cm_bottom = frame["CameraMatrix"]
    except KeyError:
        cm_bottom = None

    return [frame.number, image_bottom,
            image_top, cm_bottom, cm_top]

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
    img = PIL_Image.frombytes('YCbCr', (message.width, message.height), yuv888.tostring())
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

    filename = target_dir / (str(j) + ".png")
    img.save(filename, pnginfo=meta)

if __name__ == "__main__":
    # log_folder= "/mnt/q/2023-07-04_RC23/2023-07-08_10-30-00_HULKs_vs_Berlin_United_half1-E/game_logs/1_13_Nao0038_230708-0843"
    log_folder = sys.argv[1]
    combined_log = Path(log_folder) / "combined.log"
    if combined_log.is_file():
        # export from combined log
        log = str(combined_log)

    # TODO dont do anything if extraced stuff already exists

    my_parser = Parser()
    with LogReader(log, my_parser) as reader:
        images = map(get_images, reader.read())
        export_images(log, images)