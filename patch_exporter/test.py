import argparse
import shutil
import tempfile
from os import environ
from pathlib import Path
from typing import Optional

import cppyy
import psycopg2
from helper import Point2D, Rectangle
from label_studio_sdk import Client
from minio import Minio
from minio.commonconfig import Tags
from PatchExecutor import PatchExecutor
from tqdm import tqdm


evaluator = PatchExecutor()

output_file = "0022607.png"

with cppyy.ll.signals_as_exception():  # this could go into the other file
    frame = evaluator.convert_image_to_frame(
        str(output_file), gt_balls=list()
    )
    evaluator.set_current_frame(frame)
    evaluator.sim.executeFrame()
    evaluator.export_debug_images(frame)


rect1 = Rectangle((56, 196), (296, 436))
rect2 = Rectangle((66, 206), (286, 426))


iou1 = rect1.containment_iou(66, 206, 286, 426)
iou2 = rect2.containment_iou(56, 196, 296, 436)
print(iou1)
print(iou2)