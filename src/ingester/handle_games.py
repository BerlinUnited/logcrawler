from datetime import datetime
from pathlib import Path
import logging
import sys


def get_all_team_names(client):
    """
    Get a list of team names from the db
    """
    return {team.name: team.id for team in client.team.list()}


def check_team_name(all_teams, team_name):
    """
    Check if the name of the team that should be inserted matches the spelling of the team name in the db
    """
    return team_name in all_teams.keys()


def input_games(log_root_path, client):
    events = client.events.list()
    all_teams = get_all_team_names(client)
    for event in events:
        ev = Path(log_root_path) / event.event_folder
        all_games = [f for f in ev.iterdir() if f.is_dir()]
        for game in sorted(all_games):
            logging.warning(f"parsing folder {game}")
            if str(game.name) == "Experiments" or str(game.name) == "videos":
                logging.debug(f"ignoring {game.name} folder")
                
            try:
                game_parsed = str(game.name).split("_")
                timestamp = game_parsed[0] + "_" + game_parsed[1]
                team1 = game_parsed[2]
                team2 = game_parsed[4]
                halftime = game_parsed[5]
            except Exception as e:
                logging.error(f'{e} when parsing {game.name} folder')
                continue
            
            if not check_team_name(all_teams, team1):
                logging.warning(f"team {team1} not found in db")
                sys.exit(1)
            if not check_team_name(all_teams, team2):
                logging.warning(f"team {team2} not found in db")
                sys.exit(1)

            date_object = datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S")
            """
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
            except Exception as e:
                logging.error(f"error occured when trying to insert game {game.name}:{e}")
            """
