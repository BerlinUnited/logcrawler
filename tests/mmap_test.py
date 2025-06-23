"""
    Instead of saving all the images from a log in the filesystem lets try to use the logfile directly with mmap
"""
from google.protobuf.json_format import MessageToDict
from naoth.log import Reader as LogReader
from naoth.log import Parser
import mmap
from PIL import Image as PIL_Image
import numpy as np
import io
import time

def image_from_proto_jpeg(message):
    # hack:
    if message.format == message.JPEG:
        # unpack JPG
        img = PIL_Image.open(io.BytesIO(message.data))

        # HACK: for some reason the decoded image is inverted ...
        yuv422 = 255 - np.array(img, dtype=np.uint8)

        # flatten the image to get the same data formal like a usual yuv422
        yuv422 = yuv422.reshape(message.height * message.width * 2)
    else:
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

    # convert the image to rgb
    img = PIL_Image.frombytes(
        "YCbCr", (message.width, message.height), yuv888.tobytes()
    )
    img = img.convert("RGB")
    #img.save("test1.png")


log_path="/mnt/d/logs/2025-03-12-GO25/2025-03-13_10-10-00_BerlinUnited_vs_Bembelbots_half1/game_logs/2_36_Nao0018_250313-1032/combined.log"
file = open(log_path, 'rb')
my_parser = Parser()
my_parser.register("ImageJPEG", "Image")
my_parser.register("ImageJPEGTop", "Image")
game_log = LogReader(str(log_path), my_parser)

my_mmap = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)

for idx, frame in enumerate(game_log):

    if "ImageJPEGTop" in frame:
        position, size = frame._fields["ImageJPEGTop"]
        #print("position", position)
        #print("size", size)
        #print(frame["ImageJPEGTop"])
        start= time.time()
        data= my_mmap[position:position+size]

        message = my_parser.parse("ImageJPEGTop", bytes(data))
        end = time.time() 
        image_from_proto_jpeg(message)
        print()
        #print(message_dict)
        
        print(end - start)
        quit()