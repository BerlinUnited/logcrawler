from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.log import Parser
import os
from tqdm import tqdm
from vaapi.client import Vaapi
import traceback 

def fill_option_map(log_id):
    # TODO I could build this why parsing the BehaviorComplete representation - saving a call to the database
    try:
        response = client.behavior_option.list(
            log_id=log_id
        )
    except Exception as e:
        print(response)
        print(e)
        print("Could not fetch the list of options for this log")
        quit()
    for option in response:
        state_response = client.behavior_option_state.list(
            log_id=log_id,
            option_id=option.id,
        )
        state_dict = dict()
        for state in state_response:
            state_dict.update(
                {"id":option.id, state.xabsl_internal_state_id:state.id}
            )
        option_map.update({option.xabsl_internal_option_id: state_dict})

def get_option_id(internal_options_id):
    try:
        return option_map[internal_options_id]['id']
    except Exception as e:
        print(option_map)
        print()
        print(f"internal_options_id: {internal_options_id}")
        print()
        print(e)
        quit()

def get_state_id(internal_options_id, internal_state_id):
    try:
        state_id = option_map[internal_options_id][internal_state_id]
    except Exception as e:
        print(option_map)
        print()
        print(f"internal_options_id: {internal_options_id} - internal_state_id: {internal_state_id}")
        print()
        print(e)
        quit()
    return state_id

def parse_sparse_option(log_id, frame, time, parent, node):
    internal_options_id = node.option.id
    internal_state_id = node.option.activeState
    global_options_id = get_option_id(internal_options_id)
    global_state_id = get_state_id(internal_options_id,internal_state_id)
    json_obj = {
        "log_id":log_id,
        "options_id":global_options_id,
        "active_state":global_state_id,
        #"parent":parent, # FIXME we could make it a reference to options if we would have the root option in the db
        "frame":frame,
        #"time":time,
        #"time_of_execution":node.option.timeOfExecution,
        #"state_time":node.option.stateTime,
    }
    parse_sparse_option_list.append(json_obj)

    # iterating through sub-options
    for sub in node.option.activeSubActions:
        if sub.type == 0: # Option
            parse_sparse_option(log_id=log_id, frame=frame, time=time, parent=node.option.id, node=sub)
        elif sub.type == 2: # SymbolAssignement
            # NOTE: i don't see any benefit in saving the SymbolAssignement; the resulting value is already in the 'outputsymbols'
            pass
        else:
            # NOTE: at the moment i didn't saw any other type ?!
            print(sub)

def is_behavior_done(data):
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log_id=data.id)
        if len(response) == 0:
            return False
        log_status = response[0]
    except Exception as e:
        print(e)

    if not log_status.num_cognition_frames or int(log_status.num_cognition_frames) == 0:
        print("\tWARNING: first calculate the number of cognitions frames and put it in the db")
        return False

    print("\tcheck inserted behavior frames")
    if log_status.num_cognition_frames and int(log_status.num_cognition_frames) > 0:
        print(f"\tcognition frames are {log_status.num_cognition_frames}")
        
        response = client.behavior_frame_option.get_behavior_count(log_id=data.id)
        print(f"\tbehavior frames are {response['count']}")
        return response["count"] == int(log_status.num_cognition_frames)
    else:
        return False

if __name__ == "__main__":
    log_root_path = os.environ.get("VAT_LOG_ROOT")
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    existing_data = client.logs.list()

    def sort_key_fn(data):
        return data.log_path

    for data in sorted(existing_data, key=sort_key_fn, reverse=True):
        log_id = data.id
        log_path = Path(log_root_path) / data.log_path

        print(log_path)
        
        
        # check if we need to insert this log
        if is_behavior_done(data):
            print("\tbehavior already inserted, will continue with the next log")
            continue
        
        my_parser = Parser()
        game_log = LogReader(str(log_path), my_parser)
        parse_sparse_option_list = list()
        option_map = dict()
        
        broken_behavior = False
        for idx, frame in enumerate(tqdm(game_log, desc=f"Parsing frame", leave=True)):
            if 'FrameInfo' in frame:
                fi = frame['FrameInfo']
            else:
                print(f"frame {idx} does not have frame info representation so we dont go further")
                print("it could be that there is one more behavior frame in the next frame but this is one is not finished.")
                break

            if "BehaviorStateComplete" in frame:
                try:
                    full_behavior = frame["BehaviorStateComplete"]
                except Exception as e:
                    traceback.print_exc() 
                    print("can't parse the Behavior will continue with the next log")
                    broken_behavior = True
                    break

                for i, option in enumerate(full_behavior.options):
                    try:
                        option_response = client.behavior_option.create(
                            log_id=log_id,
                            xabsl_internal_option_id=i,
                            option_name=option.name
                        )
                    except Exception as e:
                        print(f"error inputing option from BehaviorStateComplete {log_path}")
                        print(e)
                        quit()

                    state_list = list()
                    for j, state in enumerate(option.states):
                        state_dict = {
                            "log_id":log_id,
                            "option_id":option_response.id,
                            "xabsl_internal_state_id":j,
                            "name":state.name,
                            "target":state.target,
                        }
                        state_list.append(state_dict)

                    try:
                        response = client.behavior_option_state.bulk_create(
                            repr_list=state_list
                        )
                    except Exception as e:
                        print(f"error inputing the data {log_path}")
                        print(e)
                        quit()
                fill_option_map(log_id)
            
            if "BehaviorStateSparse" in frame:
                # TODO build a check that makes sure behaviorcomplete was parsed already
                sparse_behavior = frame["BehaviorStateSparse"]
                
                for root in sparse_behavior.activeRootActions:
                    if root.type != 0: # Option
                        print("Root node must be an option!")
                    else:
                        parse_sparse_option(log_id=log_id, frame=fi.frameNumber, time=fi.time, parent=-1, node=root)
            if idx % 200 == 0:
                try:
                    response = client.behavior_frame_option.bulk_create(
                        data_list=parse_sparse_option_list
                        )
                except Exception as e:
                    print(f"error inputing the data {log_path}")
                    print(e)
                    quit()
                parse_sparse_option_list.clear()
        
        # if we abort in BehaviorStateComplete we should not do this here
        if not broken_behavior:
            try:
                response = client.behavior_frame_option.bulk_create(
                    data_list=parse_sparse_option_list
                    )
                #print(f"\t{response}")
            except Exception as e:
                print(f"error inputing the data {log_path}")
                print(e)
