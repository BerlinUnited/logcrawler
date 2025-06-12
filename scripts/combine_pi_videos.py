"""
    Video Recording from the Raspberry Pi Cam are saved as .h264 files along with the timestamp txt files.
"""
import argparse
from pathlib import Path
import subprocess

def update_timestamps_file(timestamp_file):
    #  needs to be added to the timecodes.txt file.
    expected_first_line = "# timestamp format v2"

    better_file = str(timestamp_file).replace("timestamp", "recording")

    with open(str(timestamp_file), 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if lines[0].strip() != expected_first_line.strip():
            print("\tadding timestamp header line")
            with open(str(better_file), 'w', encoding='utf-8') as file:
                file.write(expected_first_line + '\n')
                if lines:  # If there was existing content
                    file.writelines(lines)
        else:
            with open(str(better_file), 'w', encoding='utf-8') as file:
                if lines:  # If there was existing content
                    file.writelines(lines)


def main(video_folder):
    videos = Path(video_folder).glob('*.h264')
    for video_file in sorted(videos):
        #timestamp_file = str(video_file).replace("recording", "timestamp").replace("h264", "txt")
        timestamp_file = str(video_file).replace("h264", "txt")
        output_mkv_file = str(video_file).replace("h264", "mkv")
        output_mp4_file = str(video_file).replace("h264", "mp4")
        print(video_file, timestamp_file)

        update_timestamps_file(timestamp_file)

        # TODO have check for if file already exists 
        #mkvmerge -o video.mkv --timecodes 0:timecodes.txt video.h264
        if not Path(output_mkv_file).exists():
            cmd = ["mkvmerge", "-o", output_mkv_file, "--timecodes", f"0:{timestamp_file}", str(video_file)]
            print(' '.join(cmd))

            result = subprocess.run(
                cmd,
                capture_output=True,
            )
            print(result)

        # convert to mp4
        if not Path(output_mp4_file).exists():
            cmd = ["ffmpeg", "-i", output_mkv_file, "-codec", "copy", str(output_mp4_file)]
            result = subprocess.run(
                cmd,
                capture_output=True,
            )
            print(result)


if __name__ == "__main__":
    # /mnt/d/VideosGO25/combine_tests/2025-03-16-FeldA-Pi
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", type=str)
    args = parser.parse_args()

    main(args.dir)