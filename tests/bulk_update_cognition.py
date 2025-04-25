from vaapi.client import Vaapi
import os

client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

logs = client.logs.list()
def sort_key_fn(log):
    return log.id

for log in sorted(logs, key=sort_key_fn, reverse=True):
        print(f"{log.id}: {log.log_path}")

        updated_frames_list = []
        frames = client.cognitionframe.list(log=log.id)
        mframes = client.motionframe.list(log=log.id)

        for idx, frame in enumerate(frames):
            print(frame)
            json_obj = {
                "id": frame.id,
                # this has to be the id of the motionframe and must exist
                "closest_motion_frame": mframes[0].id,  # HACK use any valid motion frame id here
            }
            updated_frames_list.append(json_obj)

            if idx % 2 == 0 and idx != 0:
                response = client.cognitionframe.bulk_update(data=updated_frames_list)
                quit()
        quit()




