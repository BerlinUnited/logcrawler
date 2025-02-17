"""
    Representation Exporter
    FIXME: this fails in some logs -> add error handling and reporting about broken logs
"""
from vaapi.client import Vaapi
from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.log import Parser
from tqdm import tqdm
import os
import json


def get_representation_set_from_log(log_file_path, representation_set):
    print(f"\tparsing {log_file_path}")
    if (Path(log_file_path).is_file() and os.stat(str(log_file_path)).st_size > 0):
        my_parser = Parser()
        log = LogReader(log_file_path, my_parser)
        try:
            for frame in tqdm(log):
                dict_keys = frame.get_names()
                for key in dict_keys:
                    representation_set.add(key)
        except:
            print(f"error parsing {log_file_path}")
    
    return representation_set


if __name__ == "__main__":
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    existing_data = client.logs.list()

    def sort_key_fn(data):
        return data.log_path
    
    for data in sorted(existing_data, key=sort_key_fn):
        print(Path(data.log_path).parent)
        log_id = data.id
        log_path = Path(log_root_path) / data.log_path

        actual_log_folder = log_path.parent
        repr_json_file = actual_log_folder / "representation.json"
        # continue if json file already exists
        if not repr_json_file.is_file():
            gamelog_path = actual_log_folder / "game.log"
            combined_log_path = actual_log_folder / "combined.log"
            sensor_log_path = actual_log_folder / "sensor.log"

            logged_representation = set()
            if combined_log_path.is_file():
                logged_representation = get_representation_set_from_log(combined_log_path, logged_representation)
            else:
                logged_representation = get_representation_set_from_log(gamelog_path, logged_representation)
        
            logged_representation = get_representation_set_from_log(sensor_log_path, logged_representation)

            if len(list(logged_representation)) > 0:
                output_dict = {"representations": list(logged_representation)}

                with open(str(repr_json_file), "w", encoding="utf-8") as f:
                    json.dump(output_dict, f, ensure_ascii=False, indent=4)
        else:
            print("\trepresentation.json already exists")

        # update the database with the representations
        with open(str(repr_json_file), 'r') as file:
            # Load the content of the file into a Python dictionary
            data = json.load(file)
        response = client.logs.update(
            id=log_id,
            representation_list=data,
        )