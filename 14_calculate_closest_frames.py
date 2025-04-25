from vaapi.client import Vaapi
import os
import bisect

def test_closest_other_frames(frames,  comparison_frames):

    results = []


    for frame in frames:
        target_time = frame.frame_time
        closest_other_frame_id = None
        min_time_diff = float('inf') # Initialize with infinity


        for comparison_frame in comparison_frames:
            current_time = comparison_frame.frame_time

            # Calculate absolute time difference
        
            time_diff = abs(target_time - current_time)
            # Check if this frame is closer than the current best match
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_other_frame_id = comparison_frame.id
                best_match_time = comparison_frame.frame_time

        result_item = {}
        result_item['id'] = frame.id
        result_item['closest_other_frame'] = closest_other_frame_id
        result_item['frame_time'] = frame.frame_time
        result_item['closest_other_frame_time'] = best_match_time
        results.append(result_item)

    return results



def find_closest_other_frame(frames, comparison_frames):
    """assumes frames and comparison_frames are lists of either motion or cognition frame objects
        These lists also have to be sorted by frame_time
        returns a list of dictionaries where frame is the PK of the Motion/Cognitionframe and closest other frame 
        the PK of the closest Motion/Cognitionframe
        The time values are just for debug purposes
    """
    # create lists of values from motion or cognition frame objects since they are immutable
    cognition_times = [x.frame_time for x in comparison_frames]
    cognition_ids = [x.id for x in comparison_frames]
    
    processed_frames = []

    # go to each frame
    for frame in frames:
        current_time = frame.frame_time
        #returns the index of the leftmost postion where frame can be inserted in the comparison time list while keeping it sorted
        pos = bisect.bisect_left(cognition_times, current_time)
        # stores positions of frame_times that are next to current_time
        # example : comparison_times = [10, 20, 30] and current_time is 15
        # canditates would be [0,1] since 15 is between 10 and 20 
        candidates = []
        if pos > 0:
            candidates.append(pos - 1)
        if pos < len(cognition_times):
            candidates.append(pos)
        
        min_diff = None
        closest_id = None
        for idx in candidates:
            diff = abs(cognition_times[idx] - current_time)
            #if both candidates have the same frame_time it takes the frame with the smallest frame_id
            if min_diff is None or diff < min_diff or (diff == min_diff and cognition_ids[idx] < closest_id):
                min_diff = diff
                closest_id = cognition_ids[idx]
                closest_time = cognition_times[idx]

        processed_frame = {}

        processed_frame['id'] = frame.id
        processed_frame['closest_other_frame'] = closest_id
        processed_frame['frame_time'] = frame.frame_time
        processed_frame['closest_other_frame_time'] = closest_time
    
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

        processed_MotionFrames = find_closest_other_frame(sorted(motionframes,key=sort_frame_key_fn),sorted(cognitionframes,key=sort_frame_key_fn))

        test_MotionFrames = test_closest_other_frames(sorted(motionframes,key=sort_frame_key_fn),sorted(cognitionframes,key=sort_frame_key_fn))

        print(processed_MotionFrames==test_MotionFrames)

        processed_CognitionFrames = find_closest_other_frame(sorted(cognitionframes,key=sort_frame_key_fn),sorted(motionframes,key=sort_frame_key_fn))

        test_CognitionFrames = test_closest_other_frames(sorted(cognitionframes,key=sort_frame_key_fn),sorted(motionframes,key=sort_frame_key_fn))

        print(test_CognitionFrames==test_CognitionFrames) 




        quit()
