import subprocess
from pathlib import Path
from telemetry_parser import Parser as GPMFParser

def process_video(input_path):
    # Create output path (modify as needed)
    output_path = video_input.replace("_GoPro", "_GoPro_reencoded")
    
    if Path(output_path).exists():
        return
    # FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-map', '0:v',
        '-map', '0:a',
        '-map', '0:3',
        '-c:v', 'libx264',
        '-crf', '18',
        '-c:a', 'aac',
        '-c:s', 'copy',
        '-c:d', 'copy',
        '-movflags', '+faststart',
        output_path
    ]
    
    try:
        # Run the command
        subprocess.run(cmd, check=True)
        print(f"Successfully processed {input_path} to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {input_path}: {e}")
        quit()
    
    # TODO test telemetry
    tele = GPMFParser(output_path).telemetry()
    print(len(tele))


video_list = [
    "/mnt/repl/2025-03-12-GO25/2025-03-13_17-30-00_BerlinUnited_vs_HTWK_half1/videos/2025-03-13_17-30-00_Berlin United_vs_HTWK Robots_half1_Field-A_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-13_17-30-00_BerlinUnited_vs_HTWK_half2/videos/2025-03-13_17-30-00_Berlin United_vs_HTWK Robots_half2_Field-A_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-14_10-10-00_BerlinUnited_vs_NaoDevils_half2/videos/2025-03-14_10-10-00_Berlin United_vs_Nao Devils_half2_Field-B_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-14_15-10-00_BerlinUnited_vs_DutchNaoTeam_half1/videos/2025-03-14_15-10-00_Berlin United_vs_Dutch Nao Team_half1_Field-B_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-14_15-10-00_BerlinUnited_vs_DutchNaoTeam_half2/videos/2025-03-14_15-10-00_Berlin United_vs_Dutch Nao Team_half2_Field-B_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-15_11-40-00_BerlinUnited_vs_BHuman_half1/videos/2025-03-15_11-40-00_BerlinUnited_vs_BHuman_half1_Field-B_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-15_11-40-00_BerlinUnited_vs_BHuman_half2/videos/2025-03-15_11-40-00_BerlinUnited_vs_BHuman_half2_Field-B_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-15_15-00-00_BerlinUnited_vs_DutchNaoTeam_half1/videos/2025-03-15_15-00-00_BerlinUnited_vs_DutchNaoTeam_half1_Field-A_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-15_15-00-00_BerlinUnited_vs_DutchNaoTeam_half2/videos/2025-03-15_15-00-00_BerlinUnited_vs_DutchNaoTeam_half2_Field-A_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half1/videos/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half1_Field-B_GoPro.mp4",
    "/mnt/repl/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/videos/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2_Field-B_GoPro.mp4",
]

for video_input in video_list:
    process_video(video_input)