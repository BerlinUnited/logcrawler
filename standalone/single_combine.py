"""
Combine Image and game logs the right way
see: https://scm.cms.hu-berlin.de/berlinunited/naoth-2020/-/commit/0a79c8c2ae1143ab63f8ec907580de9eae5bc50
"""

from naoth.log import Reader as LogReader
from naoth.log import Parser
from pathlib import Path
import argparse
import os


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


def create_jpeg_image_log_dict(image_log):
    """
    Return a dictionary with frame numbers as key and image data as values.
    """
    images_by_frame = {}

    myParser = Parser()
    myParser.register("ImageJPEG", "Image")
    myParser.register("ImageJPEGTop", "Image")

    reader = LogReader(image_log, parser=myParser)

    for frame in reader.read():
        images = {}

        if "ImageJPEG" in frame.get_names():
            images["ImageJPEG"] = frame["ImageJPEG"]

        if "ImageJPEGTop" in frame.get_names():
            images["ImageJPEGTop"] = frame["ImageJPEGTop"]

        images_by_frame[frame.number] = images

    return images_by_frame


def write_combined_log_jpeg(combined_log_path, img_log_path, gamelog_path):
    image_log_index = create_jpeg_image_log_dict(str(img_log_path))

    try:
        with open(combined_log_path, "wb") as output, LogReader(gamelog_path) as reader:
            for frame in reader.read():
                # only write frames which have corresponding images
                if frame.number not in image_log_index:
                    print(
                        "Frame {} has no corresponding image data.".format(frame.number)
                    )
                    output.write(bytes(frame))
                    continue

                # contains 'ImageTop' and 'Image'
                images = image_log_index[frame.number]

                for image_repr_name, image_msg in images.items():
                    frame.add_field(image_repr_name, image_msg)

                # write the modified frame to the new log
                output.write(bytes(frame))

                # HACK: Frames are indexed by the log reader. Remove the image of already processed frames to preserve memory.
                for image_name in image_log_index[frame.number]:
                    frame.remove(image_name)
    except Exception as e:
        print(f"failed to combine file: {e}")
        # TODO set a status in the db so that no one tries to parse this again
        if combined_log_path.is_file():
            combined_log_path.unlink()


def calculate_first_image(logpath):
    """
    calculate the age of the log file. For everything prior 2023 the first image in the log is top after that its bottom
    """
    # TODO fix me, prefix is annoying here
    logpath = str(logpath)
    event = logpath.split("_")[0]
    year = int(event.split("-")[0])
    if year < 2023:
        return True
    else:
        return False


if __name__ == "__main__":
    # TODO argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input folder holding a game.log and a images.log or images_jpeg.log")

    args = parser.parse_args()

    combined_log_path = Path(args.input) / "combined.log"
    gamelog_path = Path(args.input) / "game.log"
    img_log_path = Path(args.input) / "images.log"
    img_jpeg_log_path = Path(args.input) / "images_jpeg.log"

    if not img_jpeg_log_path.exists():
        print(f"No jpeg log found in folder {img_jpeg_log_path}")
        quit()

    if not gamelog_path.exists():
        print(f"No game.log found in folder {gamelog_path}")
        quit()

    write_combined_log_jpeg(str(combined_log_path), str(img_jpeg_log_path), str(gamelog_path))
