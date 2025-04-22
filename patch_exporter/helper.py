from dataclasses import dataclass
from typing import List, Optional, Tuple
from PIL import Image as PIL_Image
import numpy as np
import tensorflow as tf
from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError
from pathlib import Path
from naoth.log import BoundingBox


@dataclass
class Frame:
    file: str
    bottom: bool
    gt_balls: List[BoundingBox]
    gt_robots: List[BoundingBox]
    gt_penalties: List[BoundingBox]
    cam_matrix_translation: Tuple[float, float, float]
    cam_matrix_rotation: np.ndarray


def load_image_as_yuv422(image_filename):
    """
    this functions loads an image from a file to the correct format for the naoth library
    """
    # don't import cv globally, because the dummy simulator shared library might need to load a non-system library
    # and we need to make sure loading the dummy simulator shared library happens first
    import cv2

    cv_img = cv2.imread(image_filename)

    # convert image for bottom to yuv422
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2YUV).tobytes()
    yuv422 = np.ndarray(480 * 640 * 2, np.uint8)
    for i in range(0, 480 * 640, 2):
        yuv422[i * 2] = cv_img[i * 3]
        yuv422[i * 2 + 1] = (cv_img[i * 3 + 1] + cv_img[i * 3 + 4]) / 2.0
        yuv422[i * 2 + 2] = cv_img[i * 3 + 3]
        yuv422[i * 2 + 3] = (cv_img[i * 3 + 2] + cv_img[i * 3 + 5]) / 2.0
    return yuv422


def load_image_as_yuv422_y_only_better(image_filename):
    im = PIL_Image.open(image_filename)
    ycbcr = im.convert("YCbCr")
    reversed_yuv888 = np.ndarray(480 * 640 * 3, "u1", ycbcr.tobytes())
    full_image_y = reversed_yuv888[0::3]
    full_image_y = full_image_y.reshape(480, 640, 1)
    half_image_y = full_image_y[::2, ::2]
    half_image_y = half_image_y / 255.0
    return half_image_y


def get_file_from_server(origin, target):
    # FIXME move to naoth python package
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


def load_model_from_server(model_name):
    get_file_from_server(f"https://models.naoth.de/{model_name}", model_name)
    return tf.keras.models.load_model(model_name)
