"""
    Representation Exporter
    FIXME: this fails in some logs -> add error handling and reporting about broken logs
"""

from pathlib import Path
from naoth.log import Reader as LogReader
from naoth.log import Parser
import psycopg2
from os import environ, stat
import json
import argparse

params = {
    "host": "pg.berlin-united.com",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get("DB_PASS"),
}
conn = psycopg2.connect(**params)
cur = conn.cursor()


def get_logs():
    select_statement = f"""
    SELECT log_path FROM robot_logs
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x[0] for x in rtn_val]
    return logs


def get_unchecked_logs():
    select_statement = f"""
    SELECT log_path FROM robot_logs WHERE representation_exists IS NULL
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    logs = [x[0] for x in rtn_val]
    return logs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--delete", action="store_true")
    parser.add_argument(
        "--all",
        help="Check all logs, by default only unchecked logs are checked",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    should_check_all = args.all

    root_path = Path(environ.get("LOG_ROOT"))
    log_list = get_logs() if should_check_all else get_unchecked_logs()

    # FIXME naming and order ist just very hard to understand
    for log_folder in sorted(log_list, reverse=True):
        print(log_folder)
        experiment_log = root_path / Path(log_folder)
        if Path(experiment_log).is_file():
            # handle the case that its an experiment and therefor the path to the file and not the folder
            actual_log_folder = root_path / Path(log_folder).parent
            output_file = actual_log_folder / str(
                Path(log_folder).name + ".representation.json"
            )
        else:
            actual_log_folder = root_path / Path(log_folder)
            output_file = actual_log_folder / "representation.json"

        if args.delete is True:
            # remove file if we want to override - this way also wrongly created files are removed even when we don't want to recreate them
            if output_file.is_file():
                output_file.unlink()

        # continue if json file already exists
        if not output_file.is_file():
            # handle experiment case
            if (
                Path(experiment_log).is_file()
                and stat(str(actual_log_folder)).st_size > 0
            ):
                logged_representation = set()
                my_parser = Parser()
                combinedlog = LogReader(experiment_log, my_parser)
                try:
                    for i, frame in enumerate(combinedlog):
                        dict_keys = frame.get_names()
                        for key in dict_keys:
                            logged_representation.add(key)
                except:
                    print("error parsing the log")
                    insert_statement = f"""
                    UPDATE robot_logs SET broken = true WHERE log_path = '{log_folder}';    
                    """
                    cur.execute(insert_statement)
                    conn.commit()
                    continue

                # only write the file if the list is not empty
                if len(list(logged_representation)) > 0:
                    output_dict = {"representations": list(logged_representation)}

                    with open(str(output_file), "w", encoding="utf-8") as f:
                        json.dump(output_dict, f, ensure_ascii=False, indent=4)
                # write to db
                insert_statement = f"""
                UPDATE robot_logs SET representation_exists = true WHERE log_path = '{log_folder}';
                UPDATE robot_logs SET broken = false WHERE log_path = '{log_folder}';    
                """
                cur.execute(insert_statement)
                conn.commit()

                # if we parse an experiment no need to check for other logfiles
                continue
            else:
                # we don't deal with image log here because we can't easily parse this the same we we can parse all other logs
                gamelog_path = actual_log_folder / "game.log"
                combined_log_path = actual_log_folder / "combined.log"
                sensor_log_path = actual_log_folder / "sensor.log"
                # TODO: I've seen cognition logs somewhere
                logged_representation = set()

                if (
                    Path(combined_log_path).is_file()
                    and stat(str(combined_log_path)).st_size > 0
                ):
                    my_parser = Parser()
                    combinedlog = LogReader(combined_log_path, my_parser)
                    try:
                        for i, frame in enumerate(combinedlog):
                            dict_keys = frame.get_names()
                            for key in dict_keys:
                                logged_representation.add(key)
                    except:
                        print("error parsing the log")
                        insert_statement = f"""
                        UPDATE robot_logs SET broken = true WHERE log_path = '{log_folder}';    
                        """
                        cur.execute(insert_statement)
                        conn.commit()
                        continue
                # case we don't have a combined log (assume here that this is fine and there is nothing to combine)
                else:
                    if (
                        Path(gamelog_path).is_file()
                        and stat(str(gamelog_path)).st_size > 0
                    ):
                        my_parser2 = Parser()
                        game_log = LogReader(gamelog_path, my_parser2)
                        try:
                            for i, frame in enumerate(game_log):
                                dict_keys = frame.get_names()
                                for key in dict_keys:
                                    logged_representation.add(key)
                        except:
                            print("error parsing the game log")
                            insert_statement = f"""
                            UPDATE robot_logs SET broken = true WHERE log_path = '{log_folder}';    
                            """
                            cur.execute(insert_statement)
                            conn.commit()
                            continue
                    # sensor log
                    if (
                        Path(sensor_log_path).is_file()
                        and stat(str(sensor_log_path)).st_size > 0
                    ):
                        my_parser3 = Parser()
                        sensor_log = LogReader(sensor_log_path, my_parser3)
                        try:
                            for i, frame in enumerate(sensor_log):
                                dict_keys = frame.get_names()
                                for key in dict_keys:
                                    logged_representation.add(key)
                        except:
                            print("error parsing the sensor log")
                            insert_statement = f"""
                            UPDATE robot_logs SET broken = true WHERE log_path = '{log_folder}';    
                            """
                            cur.execute(insert_statement)
                            conn.commit()
                            continue

                # only write the file if the list is not empty
                if len(list(logged_representation)) > 0:
                    output_dict = {"representations": list(logged_representation)}

                    with open(str(output_file), "w", encoding="utf-8") as f:
                        json.dump(output_dict, f, ensure_ascii=False, indent=4)

        # write to db
        insert_statement = f"""
        UPDATE robot_logs SET representation_exists = true WHERE log_path = '{log_folder}';
        UPDATE robot_logs SET broken = false WHERE log_path = '{log_folder}';    
        """
        cur.execute(insert_statement)
        conn.commit()
