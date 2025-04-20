from vaapi.client import Vaapi
import os

if __name__ == "__main__":
   
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    
    log = client.logs.list()

    def sort_key_fn(log):
        return log.id

    for log in sorted(log, key=sort_key_fn, reverse=True):
        print(f"{log.id}: {log.log_path}")
        
        motionframes = client.motionframe.list(log=log.id)
        cognitionframes = client.cognitionframe.list(log=log.id)

        print(len(motionframes))
        print(len(cognitionframes))

        print(motionframes[0])

        for frame in motionframes:

            #calculate closest cognition frame
            pass

        for frame in cognitionframes:
            #calculate closest motion frame
            pass

        # multiple motion frames can have the same closest cognition frame

        quit()

