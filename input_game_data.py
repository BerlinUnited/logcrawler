
from pathlib import Path
from vaapi.client import Vaapi
import os
from datetime import datetime
import logging


logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.FATAL)

#TODO check if event folder exist and return warning if not found
# split script into 3 files, add error handling check folder structure, add info to db and use logging error
if __name__ == "__main__":
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    events = client.events.list()
    for event in events:
        ev = Path(log_root_path) / event.event_folder
        all_games = [f for f in ev.iterdir() if f.is_dir()]
        for game in sorted(all_games):
            if str(game.name) == "Experiments":
                print("ignoring Experiments folder")
                # handle_experiments(event_id, game)
            elif str(game.name) == "Videos":
                print("ignoring Videos folder")
            else:
                if Path(game / 'comments.txt').is_file():
                    with open(game / 'comments.txt','r') as f:
                        comment = f.read()
                else:
                    comment = ''
                try:
                    game_parsed = str(game.name).split("_")
                    timestamp = game_parsed[0] + "_" + game_parsed[1]
                    team1 = game_parsed[2]
                    team2 = game_parsed[4]
                    halftime = game_parsed[5]
                except Exception as e:
                    logging.error(f'{e} when parsing {game.name} folder')
                    continue

                date_object = datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S")
                try:
                    print(team1)
                    response = client.games.create(
                        event=event.id,
                        team1=team1,
                        team2=team2,
                        half=halftime,
                        game_folder=str(game).removeprefix(log_root_path).strip("/"),
                        # Hack: by default django return the time with Z appended. We do that on input as well so we can compare it in the add_games function
                        # TODO: check if this is still necessary
                        start_time=date_object.isoformat() + "Z",
                        comment=comment
                    )
                except Exception as e:
                    logging.error(f"following error occured when trying to insert a game:{e}")
                exit()
                gamelog_path = Path(game) / "game_logs"
            