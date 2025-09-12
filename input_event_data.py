
from pathlib import Path
from vaapi.client import Vaapi
import os
from datetime import datetime
import logging
event_list = ["2024-07-15_RC24", "2025-03-12-GO25"]

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

#TODO check if event folder exist and return warning if not found
# split script into 3 files, add error handling check folder structure, add info to db and use logging error

#TODO write scripts that check all folders of games and create warning if team doesn't exist

#scripts should be impodent

# first check if event folder exist if no warning or error then continue
#TODO create postgres docker container script maybe psql / docker run
if __name__ == "__main__":
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    all_events = [f for f in Path(log_root_path).iterdir() if f.is_dir()]
    for event in sorted(all_events, reverse=True):
        if event.name in event_list:
            event_list.remove(event.name)
            if Path(event / 'comments.txt').is_file():
                with open(event / 'comments.txt') as f:
                    comment = f.read()
            else:
                comment = ''
            try:
                response = client.events.create(
                    name=event.name,
                    event_folder=str(event).removeprefix(log_root_path).strip("/"),
                    comment=comment
                    )
                logging.debug(f"inserted event: {event.name}")
            except Exception as e:
                logging.error(f"following error occured when trying to insert an event:{e}")

    # check if event folder that are specified in the list where found
    if len(event_list) > 0:
        for event in event_list:
            logging.warning(f"Couldn't find the {event} event folder")

            