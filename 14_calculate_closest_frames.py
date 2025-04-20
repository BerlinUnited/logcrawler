from vaapi.client import Vaapi
import os

def find_closest_time_matches(motionframes, cognitionframes):

    results = []


    for motionframe in motionframes:
        target_time = motionframe.frame_time
        closest_cognition_frame_id = None
        min_time_diff = float('inf') # Initialize with infinity


        for cognitionframe in cognitionframes:
            current_time = cognitionframe.frame_time

            # Calculate absolute time difference
            # This works directly for numbers and datetime objects
        
            time_diff = abs(target_time - current_time)
            # Check if this item2 is closer than the current best match
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_cognition_frame_id = cognitionframe.id
                best_match_time = cognitionframe.frame_time

        # Store the result for item1
        # Create a copy to avoid modifying the original list1 dictionaries
        result_item = {}
        result_item['motionframe'] = motionframe.id
        result_item['closest_cognitionframe'] = closest_cognition_frame_id
        # Store the actual time difference (could be numeric or timedelta)
        result_item['motion_time'] = motionframe.frame_time
        result_item['cognition_time'] = best_match_time
        results.append(result_item)

    return results


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

        def sort_frame_key_fn(frame):
            return frame.frame_number

        result = find_closest_time_matches(sorted(motionframes,key=sort_frame_key_fn),sorted(cognitionframes,key=sort_frame_key_fn))
        
        for x in result[:30]:
            print(f"Motion Frametime:{x['motion_time']} Cognition Frametime: {x['cognition_time']}")

        for frame in motionframes:
            # calculate closest cognition frame

            pass

        for frame in cognitionframes:
            # calculate closest motion frame
            pass

        # multiple motion frames can have the same closest cognition frame

        quit()
