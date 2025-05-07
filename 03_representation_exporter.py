"""
Representation Exporter
FIXME: this fails in some logs -> add error handling and reporting about broken logs
"""
from vaapi.client import Vaapi
import log_crawler
from pathlib import Path
import os
import json
import argparse


def is_done(log, representation_file: str, force_flag: bool) -> bool:
    if force_flag:
        print("\tforce flag is set - will parse log")
        return False

    repr_list_missing = True
    # Check if the file contains the keys we expect
    # TODO dont return yet we still need to check the data base
    if representation_file.is_file():
        with open(str(representation_file), "r") as f:
            representations = json.load(f)
            # check if we have the keys we expect in the file
            if (
                "cognition_representations" not in representations
                or "motion_representations" not in representations
            ):
                print(
                    "\tcognition_representations motion_representations field is missing in json file - will parse log"
                )
                repr_list_missing = False
    else:
        return False

    # check if data is in in the log model
    db_repr_dict = log.representation_list
    if (
        "cognition_representations" not in db_repr_dict
        or "motion_representations" not in db_repr_dict
    ):
        print(
            "\tcognition_representations motion_representations field is missing in db - will parse log"
        )
        repr_list_missing = False

    return repr_list_missing


def get_representation_set_from_log(log_file_path, representation_set):
    print(f"\tparsing {log_file_path}")
    if Path(log_file_path).is_file() and os.stat(str(log_file_path)).st_size > 0:
        representation_set = log_crawler.get_representation_set(str(log_file_path))

    return representation_set


def main(args):
    log_root_path = os.environ.get("VAT_LOG_ROOT")
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    existing_logs = client.logs.list()

    def sort_key_fn(data):
        return data.log_path

    for log in sorted(existing_logs, key=sort_key_fn, reverse=args.reverse):
        print(f"{log.id}: {log.log_path}")
        log_path = Path(log_root_path) / log.log_path

        actual_log_folder = log_path.parent
        repr_json_file = actual_log_folder / "representation.json"
        # continue if json file already exists
        if not is_done(log, repr_json_file, args.force):
            gamelog_path = actual_log_folder / "game.log"
            combined_log_path = actual_log_folder / "combined.log"
            sensor_log_path = actual_log_folder / "sensor.log"

            cognition_logged_representation = set()
            motion_logged_representation = set()
            if combined_log_path.is_file():
                cognition_logged_representation = get_representation_set_from_log(
                    combined_log_path, cognition_logged_representation
                )
            else:
                cognition_logged_representation = get_representation_set_from_log(
                    gamelog_path, cognition_logged_representation
                )

            motion_logged_representation = get_representation_set_from_log(
                sensor_log_path, motion_logged_representation
            )

            if len(list(cognition_logged_representation)) > 0:
                output_dict = {
                    "cognition_representations": list(cognition_logged_representation)
                }
                if len(list(motion_logged_representation)) > 0:
                    output_dict.update(
                        {"motion_representations": list(motion_logged_representation)}
                    )
                with open(str(repr_json_file), "w", encoding="utf-8") as f:
                    json.dump(output_dict, f, ensure_ascii=False, indent=4)

            # update the database with the representations
            with open(str(repr_json_file), "r") as file:
                # Load the content of the file into a Python dictionary
                representation_dict = json.load(file)
            client.logs.update(
                id=log.id,
                representation_list=representation_dict,
            )
        else:
            print("\trepresentation.json already exists and force flag not set")


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--force", action="store_true", default=False)
        parser.add_argument("-r", "--reverse", action="store_true", default=False)
        args = parser.parse_args()
        main(args)
    except KeyboardInterrupt:
        print("Exiting loop!")
