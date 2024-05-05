from typing import NamedTuple, Tuple, List
import numpy as np


class Point2D(NamedTuple):
    x: float
    y: float


class Rectangle(NamedTuple):
    top_left: Point2D
    bottom_right: Point2D

    def intersection_over_union(self, xtl: float, ytl: float, xbr: float, ybr: float):
        # compute x and y coordinates of the intersection rectangle
        intersection_topleft = Point2D(
            max(self.top_left[0], xtl), max(self.top_left[1], ytl))
        intersection_bottomright = Point2D(
            min(self.bottom_right[0], xbr), min(self.bottom_right[1], ybr))
        intersection = Rectangle(intersection_topleft,
                                 intersection_bottomright)

        # compute the intersection, self and other area
        intersection_area = max(0, intersection.bottom_right[0] - intersection.top_left[0] + 1) * \
                            max(0, intersection.bottom_right[1] - intersection.top_left[1] + 1)

        self_area = (self.bottom_right[0] - self.top_left[0] + 1) * \
                    (self.bottom_right[1] - self.top_left[1] + 1)
        other_area = (xbr - xtl + 1) * (ybr - ytl + 1)

        # return the intersecton over union
        return intersection_area / float(self_area + other_area - intersection_area)
    
    def chatgpt_iou(self, box1, box2):
        """
        Compute the Intersection over Union (IoU) of two bounding boxes.
        
        Args:
        - box1: A list of 4 elements [x_min, y_min, x_max, y_max].
        - box2: A list of 4 elements [x_min, y_min, x_max, y_max].
        
        Returns:
        - IoU as a float.
        """
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2

        # Calculate the intersection box
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)

        # If there's no intersection, IoU is 0
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0

        # Calculate the area of the intersection
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)

        # Calculate the area of each box
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)

        # Calculate the union area
        union_area = box1_area + box2_area - inter_area

        # IoU is intersection over union
        iou = inter_area / union_area

        return iou
    
    def containment_iou(self, xtl: float, ytl: float, xbr: float, ybr: float):
        # self is groundtruth
        x1_min, y1_min = self.top_left
        x1_max, y1_max = self.bottom_right

        if (x1_min >= xtl and y1_min >= ytl and x1_max <= xbr and y1_max <= ybr):
        # If the ground truth is fully contained within the prediction, return 1
            return 1.0
        
        return self.chatgpt_iou((xtl, ytl, xbr, ybr), (x1_min, y1_min, x1_max, y1_max))

    def get_radius(self):
        width = round((self.bottom_right[0] - self.top_left[0]) / 2)
        height = round((self.bottom_right[1] - self.top_left[1]) / 2)

        # FIXME if the patch is on the image border it should be max
        return min(width, height)

    def get_center(self):
        """
            this will calculate the center of the rectangle in the coordinate frame the coordinates are in
        """
        # FIXME if the patch is on the image border it imagine that its a square based on the max
        width = self.bottom_right[0] - self.top_left[0]
        height = self.bottom_right[1] - self.top_left[1]

        x = round(self.top_left[0] + width / 2)
        y = round(self.top_left[1] + height / 2)
        return x, y


class Frame(NamedTuple):
    file: str
    bottom: bool
    gt_balls: List[Rectangle]
    cam_matrix_translation: Tuple[float, float, float]
    cam_matrix_rotation: np.array


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