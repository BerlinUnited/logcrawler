
import os
from naoth.pb.Framework_Representations_pb2 import Image
from naoth.log import Reader as LogReader
from naoth.log import Parser

def iterate_trough_image_log():
    with open("images.log", 'rb') as f:
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
                
            frame_number = int.from_bytes(frame, byteorder='little')
            print(frame_number)
            offset = f.tell()
            # skip the image data block
            f.seek(offset + image_data_size)

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

    with open(image_log, 'rb') as f:
        # assumes the first image is a bottom image
        # NOTE: this was changed in 2023, for older image logs this might need adjustment.
        is_camera_top = first_image_is_top
        while True:
            # read the frame number
            frame = f.read(4)
            if len(frame) != 4:
                break
                
            frame_number = int.from_bytes(frame, byteorder='little')

            # read the position of the image data block
            offset = f.tell()
            # skip the image data block
            f.seek(offset + image_data_size)

            # handle the case of incomplete image at the end of the logfile
            if f.tell() >= file_size:
                print("Info: frame {} in {} incomplete, missing {} bytes. Stop."
                      .format(frame_number, image_log, f.tell() + 1 - file_size))
                print("Info: Last frame seems to be incomplete.")
                break

            if frame_number not in images_dict:
                images_dict[frame_number] = {}
            
            name = 'ImageTop' if is_camera_top else 'Image'
            images_dict[frame_number][name] = (offset, image_data_size)

            # next image is of the other cam
            is_camera_top = not is_camera_top

    return images_dict

def write_game_log_again():
    """
        this should test if I can write the game.log again and have the same data
    """
    gamelog = "game.log"
    output_log = "new_game.log"

    print(f'Writing new log to: {output_log} ...')
    with open(str(output_log), 'wb') as output, LogReader(str(gamelog)) as reader:
        for frame in reader.read():
            output.write(bytes(frame))

    # TODO check if hash and size match

def add_images_to_game_log():
    gamelog = "game.log"
    combined_log = "combined.log"
    image_logfile = "images.log"

    image_log_index = create_image_log_dict(str(image_logfile), False)

    print(f'Writing new log to: {combined_log} ...')
    with open(str(combined_log), 'wb') as output, open(str(image_logfile), 'rb') as image_log, LogReader(
            str(gamelog)) as reader:
        for frame in reader.read():
            # only write frames which have corresponding images
            if frame.number in image_log_index:
                
                # may contain 'ImageTop' and 'Image'
                for image_name, (offset, size) in image_log_index[frame.number].items():
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


if __name__ == "__main__":
    add_images_to_game_log()