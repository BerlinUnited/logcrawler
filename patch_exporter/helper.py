from dataclasses import dataclass
from typing import List, Optional, Tuple
from PIL import Image as PIL_Image
import numpy as np
import tensorflow as tf
from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError
from pathlib import Path


@dataclass
class Point2D:
    x: float
    y: float

    def __getitem__(self, index):
        assert index in (0, 1), "Index must be 0 or 1"
        return self.x if index == 0 else self.y

    def as_cv2_point(self):
        return int(self.x), int(self.y)


@dataclass
class BoundingBox:
    # FIXME this should go into our naoth python package
    top_left: Point2D
    bottom_right: Point2D

    @classmethod
    def from_coords(cls, top_left_x, top_left_y, bottom_right_x, bottom_right_y):
        return cls(
            Point2D(top_left_x, top_left_y), Point2D(bottom_right_x, bottom_right_y)
        )

    @property
    def width(self):
        return self.bottom_right.x - self.top_left.x

    @property
    def height(self):
        return self.bottom_right.y - self.top_left.y

    @property
    def area(self):
        return self.width * self.height

    @property
    def radius(self):
        width = round(self.width / 2)
        height = round(self.height / 2)

        # FIXME if the patch is on the image border it should be max
        return min(width, height)

    @property
    def center(self):
        """
        this will calculate the center of the rectangle in the coordinate frame the coordinates are in
        """
        # FIXME if the patch is on the image border it imagine that its a square based on the max

        x = round(self.top_left.x + self.width / 2)
        y = round(self.top_left.y + self.height / 2)

        return x, y

    def intersection(self, other: "BoundingBox") -> Optional["BoundingBox"]:
        """
        Calculates the intersection of this bounding box with another one.

        Returns:
            BoundingBox or None: A new BoundingBox representing the intersection,
            or None if there is no intersection.
        """
        intersect_top_left_x = max(self.top_left.x, other.top_left.x)
        intersect_top_left_y = max(self.top_left.y, other.top_left.y)
        intersect_bottom_right_x = min(self.bottom_right.x, other.bottom_right.x)
        intersect_bottom_right_y = min(self.bottom_right.y, other.bottom_right.y)

        # Check if the bounding boxes overlap
        if (
            intersect_top_left_x < intersect_bottom_right_x
            and intersect_top_left_y < intersect_bottom_right_y
        ):
            # If they do overlap, return a new BoundingBox object representing the intersection
            return BoundingBox.from_coords(
                intersect_top_left_x,
                intersect_top_left_y,
                intersect_bottom_right_x,
                intersect_bottom_right_y,
            )
        else:
            # If they don't overlap, return None
            return None


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
    ycbcr = im.convert('YCbCr')
    reversed_yuv888 = np.ndarray(480 * 640 * 3, 'u1', ycbcr.tobytes())
    full_image_y = reversed_yuv888[0::3]
    full_image_y = full_image_y.reshape(480,640,1)
    half_image_y = full_image_y[::2, ::2]
    half_image_y = half_image_y / 255.0
    return half_image_y

def get_file_from_server(origin, target):
    # FIXME move to naoth python package
    def dl_progress(count, block_size, total_size):
        print('\r', 'Progress: {0:.2%}'.format(min((count * block_size) / total_size, 1.0)), sep='', end='', flush=True)

    if not Path(target).exists():
        target_folder = Path(target).parent
        target_folder.mkdir(parents=True, exist_ok=True)
    else:
        return

    error_msg = 'URL fetch failure on {} : {} -- {}'
    try:
        try:
            urlretrieve(origin, target, dl_progress)
            print('\nFinished')
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