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
        response = client.behavior_option.list(log=log_id)
    except Exception as e:
        print(response)
        print(e)
        print("Could not fetch the list of options for this log")
        quit()
    for option in response:
        state_response = client.behavior_option_state.list(
            log=log_id,
            option_id=option.id,
        )
        state_dict = dict()
        for state in state_response:
            state_dict.update(
                {"id": option.id, state.xabsl_internal_state_id: state.id}
            )
        option_map.update({option.xabsl_internal_option_id: state_dict})


def get_option_id(internal_options_id):
    try:
        return option_map[internal_options_id]["id"]
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
        print(
            f"internal_options_id: {internal_options_id} - internal_state_id: {internal_state_id}"
        )
        print()
        print(e)
        quit()
    return state_id


def get_frame_id(target_frame_number):
    return frame_to_id.get(target_frame_number, None)


def parse_sparse_option(log_id, frame, time, parent, node):
    internal_options_id = node.option.id
    internal_state_id = node.option.activeState
    global_options_id = get_option_id(internal_options_id)
    global_state_id = get_state_id(internal_options_id, internal_state_id)

    json_obj = {
        "frame": get_frame_id(frame),
        "options_id": global_options_id,
        "active_state": global_state_id,
        # "parent":parent, # FIXME we could make it a reference to options if we would have the root option in the db
        # "frame":frame,
        # "time":time,
        # "time_of_execution":node.option.timeOfExecution,
        # "state_time":node.option.stateTime,
    }
    parse_sparse_option_list.append(json_obj)

    # iterating through sub-options
    for sub in node.option.activeSubActions:
        if sub.type == 0:  # Option
            parse_sparse_option(
                log_id=log_id, frame=frame, time=time, parent=node.option.id, node=sub
            )
        elif sub.type == 2:  # SymbolAssignement
            # NOTE: i don't see any benefit in saving the SymbolAssignement; the resulting value is already in the 'outputsymbols'
            pass
        else:
            # NOTE: at the moment i didn't saw any other type ?!
            print(sub)


def is_behavior_done(log):
    # get the log status object for this log
    try:
        # we use list here because we only know the log_id here and not the id of the logstatus object
        response = client.log_status.list(log=log.id)
        if len(response) == 0:
            return False
        log_status = response[0]
    except Exception as e:
        print(e)

    # abort if Logstatus reports no Cognition frames for this log
    if not log_status.FrameInfo or int(log_status.FrameInfo) == 0:
        print(
            "\tWARNING: first calculate the number of cognitions frames and put it in the db"
        )
        quit()

    response = client.behavior_frame_option.get_behavior_count(log=log.id)
    if int(log_status.BehaviorStateSparse) == int(response["count"]):
        return True
    elif int(response["count"]) > int(log_status.BehaviorStateSparse):
        # rust based calculation for num frames stops if one broken representation is in the last frame
        print("ERROR: there are more frames in the database than they should be")
        print(
            f"Run logstatus calculation again for log {log_id} or make sure the end of the log is calculated the same way"
        )
        print(f"\tBehaviorStateSparse frames in log are {log_status.BehaviorStateSparse}")
        print(f"\tBehaviorStateSparse frames in db are {response['count']}")
        quit()
    else:
        print(f"\tBehaviorStateSparse frames in log are {log_status.BehaviorStateSparse}")
        print(f"\tBehaviorStateSparse frames in db are {response['count']}")
        return False


if __name__ == "__main__":
    log_root_path = os.environ.get("VAT_LOG_ROOT")
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    existing_data = client.logs.list()

    def sort_key_fn(log):
        return log.id

    for log in sorted(existing_data, key=sort_key_fn, reverse=True):
        log_id = log.id
        log_path = Path(log_root_path) / log.log_path

        print(f"{log.id}: {log_path}")

        # precalculate frame mapping for this log
        frame_list = client.cognitionframe.list(log=log.id)
        # Create a dictionary mapping frame_number to id
        frame_to_id = {frame.frame_number: frame.id for frame in frame_list}

        # check if we need to insert this log
        if is_behavior_done(log):
            print("\tbehavior already inserted, will continue with the next log")
            continue

        my_parser = Parser()
        game_log = LogReader(str(log_path), my_parser)
        parse_sparse_option_list = list()
        option_map = dict()

        broken_behavior = False
        for idx, frame in enumerate(tqdm(game_log, desc="Parsing frame", leave=True)):
            if "FrameInfo" in frame:
                fi = frame["FrameInfo"]
            else:
                print(
                    f"frame {idx} does not have frame info representation so we dont go further"
                )
                print(
                    "it could be that there is one more behavior frame in the next frame but this is one is not finished."
                )
                break

            if "BehaviorStateComplete" in frame:
                try:
                    full_behavior = frame["BehaviorStateComplete"]
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    print("can't parse the Behavior will continue with the next log")
                    broken_behavior = True
                    break

                for i, option in enumerate(full_behavior.options):
                    try:
                        option_response = client.behavior_option.create(
                            log=log_id,
                            xabsl_internal_option_id=i,
                            option_name=option.name,
                        )
                    except Exception as e:
                        print(
                            f"error inputing option from BehaviorStateComplete {log_path}"
                        )
                        print(e)
                        quit()

                    state_list = list()
                    for j, state in enumerate(option.states):
                        state_dict = {
                            "log": log_id,
                            "option_id": option_response.id,
                            "xabsl_internal_state_id": j,
                            "name": state.name,
                            "target": state.target,
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
                    if root.type != 0:  # Option
                        print("Root node must be an option!")
                    else:
                        parse_sparse_option(
                            log_id=log_id,
                            frame=fi.frameNumber,
                            time=fi.time,
                            parent=-1,
                            node=root,
                        )
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
                # print(f"\t{response}")
            except Exception as e:
                print(f"error inputing the data {log_path}")
                print(e)
