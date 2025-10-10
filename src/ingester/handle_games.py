from datetime import datetime
from pathlib import Path
import logging
import sys

def check_team_name(team_name):
    # TODO implement
    return True

def input_games(log_root_path, client):
    events = client.events.list()
    for event in events:
        ev = Path(log_root_path) / event.event_folder
        all_games = [f for f in ev.iterdir() if f.is_dir()]
        for game in sorted(all_games):
            logging.debug(f"parsing folder {game}")

            try:
                game_parsed = str(game.name).split("_")
                timestamp = game_parsed[0] + "_" + game_parsed[1]
                team1 = game_parsed[2]
                team2 = game_parsed[4]
                halftime = game_parsed[5]
            except Exception as e:
                logging.error(f'{e} when parsing {game.name} folder')
                continue
            
            if not check_team_name(team1):
                sys.exit(1)
            if not check_team_name(team2):
                sys.exit(1)

            date_object = datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S")
            try:
                response = client.games.create(
                    event=event.id,
                    team1=team1,
                    team2=team2,
                    half=halftime,
                    game_folder=str(game).removeprefix(log_root_path).strip("/"),
                    start_time=date_object.isoformat(),
                    comment=comment
                )
            except Exception as e:
                logging.error(f"error occured when trying to insert game {game.name}:{e}")