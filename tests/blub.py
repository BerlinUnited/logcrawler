
from naoth.log import Parser
from PIL import Image as PIL_Image
import numpy as np
import io
import pickle

with open('filename.pickle', 'rb') as handle:
    my_message = pickle.load(handle)

my_parser = Parser()
my_parser.register("ImageJPEG"   , "Image")
my_parser.register("ImageJPEGTop", "Image")

message = my_parser.parse("ImageJPEGTop", bytes(my_message))

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
print(yuv888.dtype, y.dtype)

# convert the image to rgb
img = PIL_Image.frombytes('YCbCr', (message.width, message.height), yuv888.tobytes())
img = img.convert("RGB")
img.save("0.png")