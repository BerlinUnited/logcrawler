"""
    Combine Image and game logs the right way
    see: https://scm.cms.hu-berlin.de/berlinunited/naoth-2020/-/commit/0a79c8c2ae1143ab63f8ec907580de9eae5bc50

    # TODO: we have stuff like this: /vol/repl261-vol4/naoth/logs/2023-08-cccamp/2023-08-18-testgame_04/2_22_Nao0004_230818-1213
    were we only have an image log and no game.log
"""

from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.pb.Framework_Representations_pb2 import Image
import psycopg2
from os import environ, stat
import os
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

# this is for making it easier to test something in another table
db_name = "robot_logs" # experiment_logs or robot_logs

def create_image_log_dict(image_log, first_image_is_top):
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
                break

            if frame_number not in images_dict:
                images_dict[frame_number] = {}

            name = "ImageTop" if is_camera_top else "Image"
            images_dict[frame_number][name] = (offset, image_data_size)

            # next image is of the other cam
            is_camera_top = not is_camera_top

    return images_dict


def get_logs():
    select_statement = f"""
    SELECT log_path FROM {db_name}
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x[0] for x in rtn_val]
    return logs

def calculate_first_image(logpath):
    """
    calculate the age of the log file. For everything prior 2023 the first image in the log is top after that its bottom
    """
    event = logpath.split("_")[0]
    year = int(event.split("-")[0])
    if year < 2023:
        return True
    else:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delete", action="store_true")
    args = parser.parse_args()

    root_path = Path(environ.get('LOG_ROOT'))
    # FIXME now log list can contain folders and actual logs
    log_list = get_logs()

    if args.delete is True:
        # we delete all combined logs in an extra loop,
        # this the combine loop later can be disrupted without needing to do all the work again in case of overwrite
        for log in log_list:
            print(log)
            actual_log_folder = root_path / Path(log)
            if Path(actual_log_folder).is_file():
                print("\tpath is a experiment log - there wont be a combined file here - nothing to delete")
                continue
            
            combined_log_path = actual_log_folder / "combined.log"
            # remove file if we want to override - this way also wrongly created files are removed even when we don't want to recreate them
            if combined_log_path.is_file():
                print("\tdeleting the combined log")
                combined_log_path.unlink()

    for log in sorted(log_list):
        print(log)
        actual_log_folder = root_path / Path(log)
        if Path(actual_log_folder).is_file():
            print("\tpath is a experiment log - no automatic combining here. If needed combine the log manually and add to the event list")
            continue
        combined_log_path = actual_log_folder / "combined.log"
        gamelog_path = actual_log_folder / "game.log"
        img_log_path = actual_log_folder / "images.log"
        
        if not (
            Path(gamelog_path).is_file()
            and stat(str(gamelog_path)).st_size > 0
            and Path(img_log_path).is_file()
            and stat(str(img_log_path)).st_size > 0
        ):
            print("\tcan't combine anything here")
            insert_statement = f"""
            UPDATE {db_name} SET combined_status = false WHERE log_path = '{log}';
            """
            cur.execute(insert_statement)
            conn.commit()
            continue


        if not combined_log_path.is_file():
            is_first_image_top = calculate_first_image(log)
            image_log_index = create_image_log_dict(str(img_log_path), first_image_is_top=is_first_image_top)
            try:
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
            except:
                print("failed to combine file")
                # TODO set a status in the db so that no one tries to parse this again
                # check 2023-08-cccamp/2023-08-17_12-00-00_Berlin United_vs_TestOpponent_testgame-02/game_logs/1_21_Nao0041_230817-1136
                # Maybe we can handle weird broken files better than completely ignoring them??
                if combined_log_path.is_file():
                    combined_log_path.unlink()

        # insert in db if the file exists - so combining was successful
        if combined_log_path.is_file():
            print("\tset combined status to true")
            insert_statement = f"""
            UPDATE {db_name} SET combined_status = true WHERE log_path = '{log}';
            """
            cur.execute(insert_statement)
            conn.commit()