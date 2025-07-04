"""
This script should put all necessary data from one event into the database
"""

from pathlib import Path
from vaapi.client import Vaapi
import os
from datetime import datetime

event_list = ["2024-07-15_RC24", "2025-03-12-GO25"]


def handle_games(event_id: int, game: str):
    # for now we allow only on folder called Experiments to also exist inside the Event folder -> TODO have discussion about additional folders

    # parse additional information from game folder
    try:
        game_parsed = str(game.name).split("_")
        timestamp = game_parsed[0] + "_" + game_parsed[1]
        team1 = game_parsed[2]
        team2 = game_parsed[4]
        halftime = game_parsed[5]
    except Exception as e:
        print(e)
        print(game_parsed)

    date_object = datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S")

    response = client.games.create(
        event=event_id,
        team1=team1,
        team2=team2,
        half=halftime,
        game_folder=str(game).removeprefix(log_root_path).strip("/"),
        # Hack: by default django return the time with Z appended. We do that on input as well so we can compare it in the add_games function
        # TODO: check if this is still necessary
        start_time=date_object.isoformat() + "Z",
    )
    return response


def handle_experiments(event_id: int, experiment_folder: str):
    # TODO make sure it only looks at logfiles
    for logfile in [f for f in experiment_folder.iterdir() if f.is_file()]:
        exp_response = client.experiment.create(
            event_id=event_id,
            name=logfile.name,
        )
        print(exp_response)

        response = client.logs.create(
            log_experiment=exp_response.id,
            log_path=logfile.name,
        )
        print(response)


def get_robot_version(head_number: str) -> str:
    head_number = int(head_number)

    if head_number > 90:
        return "v5"
    elif head_number < 40:
        return "v6"
    else:
        assert False, f"Unexpected head_number value: {head_number}"


if __name__ == "__main__":
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    all_events = [f for f in Path(log_root_path).iterdir() if f.is_dir()]
    for event in sorted(all_events, reverse=True):
        if event.name in event_list:
            response = client.events.create(
                name=event.name,
                event_folder=str(event).removeprefix(log_root_path).strip("/"),
                )
            event_id = response.id

            all_games = [f for f in event.iterdir() if f.is_dir()]
            for game in sorted(all_games):
                if str(game.name) == "Experiments":
                    print("ignoring Experiments folder")
                    # handle_experiments(event_id, game)
                elif str(game.name) == "Videos":
                    print("ignoring Videos folder")
                else:
                    print(f"{game}")
                    response = handle_games(event_id, game)
                    game_id = response.id

                    gamelog_path = Path(game) / "game_logs"
                    all_logs = [f for f in gamelog_path.iterdir() if f.is_dir()]
                    for logfolder in sorted(all_logs):
                        print(f"\t{logfolder}")
                        logfolder_parsed = str(logfolder.name).split("_")
                        playernumber = logfolder_parsed[0]
                        head_number = logfolder_parsed[1]
                        version = get_robot_version(head_number)
                        nao_config_file = Path(logfolder) / "nao.info"
                        with open(str(nao_config_file), "r") as file:
                            # Read all lines from the file
                            lines = file.readlines()

                            # Extract the first and third lines
                            body_serial = lines[
                                0
                            ].strip()  # Strip to remove any trailing newline characters
                            head_serial = lines[2].strip()

                        log_path = (
                            str(Path(logfolder) / "game.log")
                            .removeprefix(log_root_path)
                            .strip("/")
                        )
                        combined_log_path = (
                            str(Path(logfolder) / "combined.log")
                            .removeprefix(log_root_path)
                            .strip("/")
                        )
                        sensor_log_path = (
                            str(Path(logfolder) / "sensor.log")
                            .removeprefix(log_root_path)
                            .strip("/")
                        )
                        

                        try:
                            response = client.logs.create(
                                game=game_id,
                                robot_version=version,
                                player_number=int(playernumber),
                                head_number=int(head_number),
                                body_serial=body_serial,
                                head_serial=head_serial,
                                log_path=log_path,
                                combined_log_path=combined_log_path,
                                sensor_log_path=sensor_log_path,
                            )
                        except Exception as e:
                            print("ERROR:", e)
                            continue

                        # patch game object for testgame flag
                        try:
                            if "test" in log_path.lower():
                                testgame_flag = True
                            else:
                                testgame_flag = False

                            client.games.update(
                                id=game_id,
                                is_testgame=False
                            )
                        except Exception as e:
                            print("ERROR:", e)
                            quit()

                        # get log id of the newly created log object
                        log_id = response.id

                        # create an empty log status object here
                        response = client.log_status.create(
                            log=log_id,
                        )
