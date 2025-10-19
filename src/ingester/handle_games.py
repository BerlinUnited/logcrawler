from typing import Dict, Mapping
from datetime import datetime
from pathlib import Path
import logging
import sys


def get_all_team_names(client) -> Dict[str, int]:
    """
    Get a list of team names from the db
    """
    return {team.name: team.id for team in client.team.list()}


def check_team_name(all_teams: Mapping[str, int], team_name: str) -> bool:
    """
    Check if the name of the team that should be inserted matches the spelling of the team name in the db
    """
    return team_name in all_teams.keys()

def get_game_comment(game):
    if Path(game / 'comments.txt').is_file():
        with open(game / 'comments.txt') as f:
            comment = f.read()
    else:
        logging.warning(f"No comments.txt found for game {game.name}")
        comment = ''
    return comment


def input_games(log_root_path, client):
    events = client.events.list()
    all_teams = get_all_team_names(client)
    for event in events:
        ev = Path(log_root_path) / event.event_folder
        all_games = [f for f in ev.iterdir() if f.is_dir()]
        for game in sorted(all_games):
            logging.debug(f"parsing folder {game}")
            if str(game.name) == "experiments" or str(game.name) == "videos" or str(game.name) == "gc_logs" or str(game.name) == "tcm_logs":
                logging.debug(f"ignoring {game.name} folder")
                continue

            try:
                game_parsed = str(game.name).split("_")
                timestamp = game_parsed[0] + "_" + game_parsed[1]
                team1 = game_parsed[2]
                team2 = game_parsed[4]
                halftime = game_parsed[5]
            except Exception as e:
                logging.error(f'{e} when parsing {game.name} folder in {event.event_folder}')
                continue
            
            if not check_team_name(all_teams, team1):
                logging.error(f"team {team1} not found in db")
                continue
            if not check_team_name(all_teams, team2):
                logging.error(f"team {team2} not found in db")
                continue

            date_object = datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S")
            
            # TODO check for comments here
            comment = get_game_comment(game)

            try:
                response = client.games.create(
                    event=event.id,
                    team1=all_teams[team1],
                    team2=all_teams[team2],
                    half=halftime,
                    game_folder=str(game).removeprefix(log_root_path).strip("/"),
                    start_time=date_object.isoformat(),
                    comment=comment
                )
                logging.info(f"successfully inserted {game.name} in db")
            except Exception as e:
                logging.error(f"error occured when trying to insert game {game.name}:{e}")
            sys.exit(1)
