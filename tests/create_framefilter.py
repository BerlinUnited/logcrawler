"""
Create a frame filter for testing
"""
from vaapi.client import Vaapi
import os


def frame_filter_demo(client):
    log_id = 282
    # TODO find all image with annotations
    response= client.annotations.list(log=log_id)

    frame_list = set([i.frame_number for i in response])

    # publish the frames list
    resp = client.frame_filter.create(
        log_id=log_id,
        name="my_cool_filter",
        frames={"frame_list": list(frame_list)},
    )
    print(resp)


if __name__ == "__main__":
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    frame_filter_demo(client)
