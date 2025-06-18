"""
    iterate over all videos and upload them - Name and description is based on file name and other data from the db
    after upload the url should be written in the video model
"""
from vaapi.client import Vaapi
from uploader import check_files, get_authenticated_service, initialize_upload_simple
from pathlib import Path
import os


def main():
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    check_files()
    youtube = get_authenticated_service()

    def sort_key_fn(video):
        return video.video_path

    videos = client.video.list()
    for video in sorted(videos, key=sort_key_fn):
        print(video.video_path)
        # only upload if we dont have the url saved in the db
        if video.url is not None:
            continue

        print(Path(video.video_path).name)
        title = str(Path(video.video_path).stem)

        video_file = Path(log_root_path) / Path(video.video_path)
        # Playlist ID ist for German Open 2025
        upload_response = initialize_upload_simple(youtube, videofile=str(video_file), title=title, description="", playlistId="PLVoczrk_MzTwHKCQ0ZI9pirjBQZjwV-gM")
        
        # patch the video model with url
        youtube_url = "https://www.youtube.com/watch?v=" + upload_response['id']
        response = client.video.update(id=video.id, url=youtube_url)


if __name__ == "__main__":
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    main()
