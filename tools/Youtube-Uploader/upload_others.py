"""
    iterate over all videos and upload them - Name and description is based on file name and other data from the db
    after upload the url should be written in the video model
"""
from vaapi.client import Vaapi
from uploader import check_files, get_authenticated_service, initialize_upload_simple
from pathlib import Path
import os

# TODO how to make sure not to upload twice - we cant query the api for uploaded videos

def main():
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    check_files()
    youtube = get_authenticated_service()

    german_open = client.events.get(2)

    video_folder = Path(log_root_path) / german_open.event_folder / "videos"
    videos = Path(video_folder).glob('*.mp4')



    for video in sorted(videos):
        #
        title = str(Path(video).stem)
        if not title.startswith("2025-03-16_12"):
            continue
        print(str(video))
        # Playlist ID ist for German Open 2025
        upload_response = initialize_upload_simple(youtube, videofile=str(video), title=title, description="", playlistId="PLVoczrk_MzTwHKCQ0ZI9pirjBQZjwV-gM")
        print(upload_response)


if __name__ == "__main__":
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    main()
