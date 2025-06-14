"""
add videos to the database
"""

from vaapi.client import Vaapi
from pathlib import Path
import os


def main():
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    games = client.games.list(event=2)
    for game in games:
        game_folder = Path(log_root_path) / game.game_folder
        print(game_folder)

        video_folder = Path(game_folder) / "videos"
        if not video_folder.exists():
            continue

        all_videos = [f for f in video_folder.iterdir()]
        # print(f"\t{all_videos}")
        for video in all_videos:
            video_path = str(video).removeprefix(log_root_path).strip("/")
            print(f"\t{video_path}")
            video_parsed = str(video.name).split("_")
            type = Path(video_parsed[7]).stem  # removes the .mp4 ending
            
            #print(str(video).removeprefix(log_root_path).strip("/"))
            response = client.video.create(game=game.id, video_path=video_path, type=str(type))



if __name__ == "__main__":
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    main()
