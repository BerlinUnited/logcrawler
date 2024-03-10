"""
    Combine Image and game logs the right way
    see: https://scm.cms.hu-berlin.de/berlinunited/naoth-2020/-/commit/0a79c8c2ae1143ab63f8ec907580de9eae5bc509
"""

from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.log import Parser
from naoth.pb.Framework_Representations_pb2 import Image
import psycopg2
from os import environ, stat
import os


params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": "fsdjhwzuertuqg",
}
conn = psycopg2.connect(**params)
cur = conn.cursor()


def create_image_log_dict(image_log, first_image_is_top=True):
    """
    Return a dictionary with frame numbers as key and (offset, size, is_camera_bottom) tuples of image data as values.
    """
    # parse image log
    width = 640
    height = 480
    bytes_per_pixel = 2
    image_data_size = width * height * bytes_per_pixel

    file_size = os.path.getsize(image_log)

    images_dict = dict()

    with open(image_log, "rb") as f:
        # assumes the first image is a bottom image
        # NOTE: this was changed in 2023, for older image logs this might need adjustment.
        is_camera_top = first_image_is_top
        while True:
            # read the frame number
            frame = f.read(4)
            if len(frame) != 4:
                break

            frame_number = int.from_bytes(frame, byteorder="little")

            # read the position of the image data block
            offset = f.tell()
            # skip the image data block
            f.seek(offset + image_data_size)

            # handle the case of incomplete image at the end of the logfile
            if f.tell() >= file_size:
                print(
                    "Info: frame {} in {} incomplete, missing {} bytes. Stop.".format(
                        frame_number, image_log, f.tell() + 1 - file_size
                    )
                )
                print("Info: Last frame seems to be incomplete.")
                break

            if frame_number not in images_dict:
                images_dict[frame_number] = {}

            name = "ImageTop" if is_camera_top else "Image"
            images_dict[frame_number][name] = (offset, image_data_size)

            # next image is of the other cam
            is_camera_top = not is_camera_top

    return images_dict


def get_logs():
    # FIXME i could create two functions like this one for each version of the combine script
    select_statement = f"""
    SELECT log_path FROM robot_logs
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x[0] for x in rtn_val]
    return logs


if __name__ == "__main__":
    root_path = (
        environ.get("LOG_ROOT") or "/mnt/q/"
    )  # use or with environment variable to make sure it works in k8s as well
    root_path = Path(root_path)
    log_list = get_logs()
    overwrite = False
    for log_folder in log_list:
        actual_log_folder = root_path / Path(log_folder)
        combined_log_path = actual_log_folder / "combined.log"
        gamelog_path = actual_log_folder / "game.log"
        img_log_path = actual_log_folder / "images.log"
        sensor_log_path = actual_log_folder / "sensor.log"
        print(log_folder)

        if not (
            Path(gamelog_path).is_file()
            and stat(str(gamelog_path)).st_size > 0
            and Path(img_log_path).is_file()
            and stat(str(img_log_path)).st_size > 0
        ):
            print("can't combine anything here")
            insert_statement = f"""
            UPDATE robot_logs SET combined_status = false WHERE log_path = '{log_folder}';
            """
            cur.execute(insert_statement)
            conn.commit()
            continue

        if overwrite is True:
            # remove file if we want to override - this way also wrongly created files are removed even when we don't want to recreate them
            if combined_log_path.is_file():
                combined_log_path.unlink()

        if not combined_log_path.is_file():
            image_log_index = create_image_log_dict(str(img_log_path), False)
            # FIXME I could add sensor log to combined log as well
            with open(str(combined_log_path), "wb") as output, open(
                str(img_log_path), "rb"
            ) as image_log, LogReader(str(gamelog_path)) as reader:
                for frame in reader.read():
                    # only write frames which have corresponding images
                    if frame.number in image_log_index:

                        # may contain 'ImageTop' and 'Image'
                        for image_name, (offset, size) in image_log_index[
                            frame.number
                        ].items():
                            # load image data
                            image_log.seek(offset)
                            image_data = image_log.read(size)

                            # add image from image.log
                            msg = Image()
                            msg.height = 480
                            msg.width = 640
                            msg.format = Image.YUV422
                            msg.data = image_data

                            frame.add_field(image_name, msg)

                        # write the modified frame to the new log
                        output.write(bytes(frame))

                        # HACK: Frames are indexed by the log reader. Remove the image of already processed frames to preserve memory.
                        for image_name in image_log_index[frame.number]:
                            frame.remove(image_name)

                    else:
                        # write unmodified frame from game.log to the new log
                        output.write(bytes(frame))

        # insert in db if the file exists - so combining was successful
        if combined_log_path.is_file():
            insert_statement = f"""
            UPDATE robot_logs SET combined_status = true WHERE log_path = '{log_folder}';
            """
            cur.execute(insert_statement)
            conn.commit()