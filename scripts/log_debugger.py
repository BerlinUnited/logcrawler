import os
from naoth.pb.Framework_Representations_pb2 import Image
from naoth.log import Reader as LogReader

from pathlib import Path
from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError


def iterate_trough_image_log():
    with open("images.log", "rb") as f:
        width = 640
        height = 480
        bytes_per_pixel = 2
        image_data_size = width * height * bytes_per_pixel
        # NOTE: this was changed in 2023, for older image logs this might need adjustment.
        while True:
            # read the frame number
            frame = f.read(4)
            if len(frame) != 4:
                break

            frame_number = int.from_bytes(frame, byteorder="little")
            print(frame_number)
            offset = f.tell()
            # skip the image data block
            f.seek(offset + image_data_size)


def get_dataset_from_server(origin, target):
    # https://datasets.naoth.de/rc19_classification_16_bw_bottom.pkl
    def dl_progress(count, block_size, total_size):
        print(
            "\r",
            "Progress: {0:.2%}".format(min((count * block_size) / total_size, 1.0)),
            sep="",
            end="",
            flush=True,
        )

    if not Path(target).exists():
        target_folder = Path(target).parent
        target_folder.mkdir(parents=True, exist_ok=True)
    else:
        return

    error_msg = "URL fetch failure on {} : {} -- {}"
    try:
        try:
            urlretrieve(origin, target, dl_progress)
            print("\nFinished")
        except HTTPError as e:
            raise Exception(error_msg.format(origin, e.code, e.reason))
        except URLError as e:
            raise Exception(error_msg.format(origin, e.errno, e.reason))
    except (Exception, KeyboardInterrupt):
        if Path(target).exists():
            Path(target).unlink()
        raise


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


def combine_all_logs():
    game_log = "game.log"
    image_log = "images.log"
    combined_log_path = "combined.log"

    get_dataset_from_server(
        "https://logs.naoth.de/2024-lab_tests/2024-05-10_17-00-00_Berlin%20United_vs_BerlinUnited_half1/game_logs/1_26_Nao0028_240510-1520/game.log",
        game_log,
    )
    get_dataset_from_server(
        "https://logs.naoth.de/2024-lab_tests/2024-05-10_17-00-00_Berlin%20United_vs_BerlinUnited_half1/game_logs/1_26_Nao0028_240510-1520/images.log",
        image_log,
    )
    is_first_image_top = False
    image_log_index = create_image_log_dict(
        str(image_log), first_image_is_top=is_first_image_top
    )
    with open(str(combined_log_path), "wb") as output, open(
        str(image_log), "rb"
    ) as image_log, LogReader(str(game_log)) as gamelog_reader:
        for frame in gamelog_reader.read():
            print(frame.number)
            # only write frames which have corresponding images
            if frame.number in image_log_index:

                # may contain 'ImageTop' and 'Image'
                for image_name, (offset, size) in image_log_index[frame.number].items():
                    print(image_name)
                    print()
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


def sensor_log():
    sensor_log = "sensor.log"
    with LogReader(str(sensor_log)) as sensorlog_reader:
        for frame in sensorlog_reader.read():
            print(frame.number)


if __name__ == "__main__":
    # Sensor logs have very different frame numbers so we cant easily combine them
    # sensor_log()
    combine_all_logs()
