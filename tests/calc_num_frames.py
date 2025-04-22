from naoth.log import Reader as LogReader
from naoth.log import Parser

my_parser = Parser()
my_parser.register("ImageTop", "Image")
my_parser.register("ImageJPEG", "Image")
my_parser.register("ImageJPEGTop", "Image")

combined_log_path = "/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/combined.log"

game_log = LogReader(str(combined_log_path), my_parser)
for frame in game_log:
    # stop parsing log if FrameInfo is missing
    try:
        frame_number = frame["FrameInfo"].frameNumber
        print(frame_number)
    except Exception as e:
        print(e)
        quit()
