"""
    Image Extractor
"""

from pathlib import Path
import numpy as np
from PIL import PngImagePlugin
from PIL import Image as PIL_Image
from naoth.log import Reader as LogReader
from naoth.log import Parser
from os import environ
import psycopg2
import shutil
import argparse


params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get('DB_PASS')
}
conn = psycopg2.connect(**params)
cur = conn.cursor()


def export_images(logfile, img, output_folder_top, output_folder_bottom):
    """
    creates two folders:
        <logfile name>_top
        <logfile name>_bottom

    and saves the images inside those folders
    """

    for i, img_b, img_t, cm_b, cm_t in img:
        frame_number = format(
            i, "07d"
        )  # make frame number a fixed length string so that the images are in the correct order
        if img_b:
            img_b = img_b.convert("RGB")
            save_image_to_png(
                frame_number, img_b, cm_b, output_folder_bottom, cam_id=1, name=logfile
            )

        if img_t:
            img_t = img_t.convert("RGB")
            save_image_to_png(
                frame_number, img_t, cm_t, output_folder_top, cam_id=0, name=logfile
            )

        print("\tsaving images from frame ", i, end="\r", flush=True)


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

    return [frame.number, image_bottom, image_top, cm_bottom, cm_top]


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
        "YCbCr", (message.width, message.height), yuv888.tostring()
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

    filename = target_dir / (str(j) + ".png")
    img.save(filename, pnginfo=meta)


def get_logs():
    select_statement = f"""
    SELECT log_path FROM robot_logs WHERE images_exist = true
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x[0] for x in rtn_val]
    return logs


def delete_everything(log_list):
    # FIXME: cant handle experiment logs yet
    for log_folder in log_list:
        actual_log_folder = root_path / Path(log_folder)
        extracted_folder = (
            Path(actual_log_folder).parent.parent
            / Path("extracted")
            / Path(actual_log_folder).name
        )
        output_folder_top = extracted_folder / Path("log_top")
        output_folder_bottom = extracted_folder / Path("log_bottom")
        print(f"deleting images for {log_folder}")
        if output_folder_top.exists():
            shutil.rmtree(output_folder_top)

        if output_folder_bottom.exists():
            shutil.rmtree(output_folder_bottom)


def calculate_output_path(log_folder: str):
    log_path_w_prefix = root_path / Path(log_folder)
    if Path(log_path_w_prefix).is_file():
        print("\tdetected experiment log")
        actual_log_folder = root_path / Path(log_folder).parent
        log = log_path_w_prefix

        extracted_folder = (
            Path(actual_log_folder)
            / Path("extracted")
            / Path(log_path_w_prefix).stem
        )
        output_folder_top = extracted_folder / Path("log_top")
        output_folder_bottom = extracted_folder / Path("log_bottom")

        print(f"\toutput folder will be {extracted_folder}")
    else:
        print("\tdetected normal game log")
        actual_log_folder = root_path / Path(log_folder)
        combined_log = root_path / Path(actual_log_folder) / "combined.log"
        game_log = root_path / Path(actual_log_folder) / "game.log"
        if combined_log.is_file():
            log = combined_log
        elif game_log.is_file():
            log = log = combined_log
        else:
            log = None

        extracted_folder = (
            Path(actual_log_folder).parent.parent
            / Path("extracted")
            / Path(actual_log_folder).name
        )

        output_folder_top = extracted_folder / Path("log_top")
        output_folder_bottom = extracted_folder / Path("log_bottom")
    
    return log, output_folder_top, output_folder_bottom

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delete", action="store_true")
    args = parser.parse_args()

    root_path = Path(environ.get("LOG_ROOT"))  
    log_list = get_logs()

    if args.delete is True:
        delete_everything(log_list)

    for log_folder in log_list:
        print(log_folder)
        log, out_top, out_bottom = calculate_output_path(log_folder)
        if log is None:
            continue

        # dont do anything if extraced stuff already exists
        if out_top.exists() and out_bottom.exists():
            pass
        else:
            out_top.mkdir(exist_ok=True, parents=True)
            out_bottom.mkdir(exist_ok=True, parents=True)

            my_parser = Parser()
            with LogReader(log, my_parser) as reader:
                images = map(get_images, reader.read())
                export_images(log, images, out_top, out_bottom)

        # write to db
        insert_statement = f"""
        UPDATE robot_logs SET extract_status = true WHERE log_path = '{log_folder}';
        """
        cur.execute(insert_statement)
        conn.commit()
