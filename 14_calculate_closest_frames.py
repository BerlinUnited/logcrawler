from vaapi.client import Vaapi
import os
import bisect

def find_closest_other_frame(frames, comparison_frame,mode):
    # Sort list_b by frame_time and prepare helper lists
    cognition_times = [x.frame_time for x in comparison_frame]
    cognition_ids = [x.id for x in comparison_frame]
    
    processed_frames = []

    # Process each element in list_a to find closest in list_b
    for frame in frames:
        current_time = frame.frame_time
        pos = bisect.bisect_left(cognition_times, current_time)
        candidates = []
        if pos > 0:
            candidates.append(pos - 1)
        if pos < len(cognition_times):
            candidates.append(pos)
        
        min_diff = None
        closest_id = None
        for idx in candidates:
            diff = abs(cognition_times[idx] - current_time)
            if min_diff is None or diff < min_diff or (diff == min_diff and cognition_ids[idx] < closest_id):
                min_diff = diff
                closest_id = cognition_ids[idx]
                closest_time = cognition_times[idx]

        processed_frame = {}

        if mode == "motion":
            processed_frame['motionframe'] = frame.id
            processed_frame['closest_cognition_frame'] = closest_id
            processed_frame['motion_time'] = frame.frame_time
            processed_frame['cognition_time'] = closest_time
        elif mode == "cognition":
            processed_frame['cognitionframe'] = frame.id
            processed_frame['closest_motion_frame'] = closest_id
            processed_frame['cognition_time'] = frame.frame_time
            processed_frame['motion_time'] = closest_time
        processed_frames.append(processed_frame)

    return processed_frames



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
            return frame.frame_time

        processed_MotionFrames = find_closest_other_frame(sorted(motionframes,key=sort_frame_key_fn),sorted(cognitionframes,key=sort_frame_key_fn),"motion")
        processed_CognitionFrames = find_closest_other_frame(sorted(cognitionframes,key=sort_frame_key_fn),sorted(motionframes,key=sort_frame_key_fn),"cognition")

        for frame in processed_MotionFrames[:100]:
            print(frame)

        print()
        print()
        
        for frame in processed_CognitionFrames[:100]:
            print(frame)

        quit()
