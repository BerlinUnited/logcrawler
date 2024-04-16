import psycopg2
from pathlib import Path
from os import environ
import argparse
from event_list import event_list, experiment_list

# connect to database
params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get('DB_PASS')
}
conn = psycopg2.connect(**params)
cur = conn.cursor()

def cleanup():
    cur.execute("DROP TABLE robot_logs")

def create_log_table(db_name: str):
    # log_path is the unique identifier of the row
    sql_query = f"""
    CREATE TABLE IF NOT EXISTS {db_name} (
        log_path VARCHAR, 
        event_name VARCHAR,
        half VARCHAR,
        robot_version VARCHAR,
        playernumber INT,
        headnumber INT,
        bodynumber VARCHAR,
        team1 VARCHAR,
        team2 VARCHAR,
        time timestamp,
        broken BOOLEAN DEFAULT FALSE,
        representation_exists BOOLEAN,
        images_exist BOOLEAN,
        combined_status BOOLEAN,
        extract_status BOOLEAN,
        bucket_top VARCHAR,
        bucket_top_patches VARCHAR,
        bucket_bottom VARCHAR,
        bucket_bottom_patches VARCHAR,
        labelstudio_project VARCHAR,
        ls_project_bottom VARCHAR,
        ls_project_top  VARCHAR,
        bottom_validated BOOLEAN,
        top_validated BOOLEAN,
        CONSTRAINT my_constraint_{db_name} UNIQUE (log_path)
    );
    """
    cur.execute(sql_query)
    conn.commit()

def insert_log_data():
    root_path = environ.get('LOG_ROOT')
    for event in [f for f in Path(root_path).iterdir() if f.is_dir()]:
        if event.name in event_list:
            print(event)
            for game in [f for f in event.iterdir() if f.is_dir()]:
                print(f"\t{game}")
                # for now we allow only on folder called Experiments to also exist inside the Event folder -> TODO have discussion about additional folders
                if str(game.name) == "Experiments":
                    continue
                # parse additional information from game folder
                game_parsed = str(game.name).split("_")
                timestamp = game_parsed[0] + "_" + game_parsed[1]
                team1 = game_parsed[2]
                team2 = game_parsed[4]
                halftime = game_parsed[5]

                gamelog_path = Path(game) / "game_logs"
                
                for logfolder in [f for f in gamelog_path.iterdir() if f.is_dir()]:
                    print(f"\t\t{logfolder}")
                    logfolder_parsed = str(logfolder.name).split("_")
                    playernumber = logfolder_parsed[0]
                    head_number = logfolder_parsed[1]
                    body_number = logfolder_parsed[2]

                    # its really important that logfolder does not have a leading slash
                    logfolder_w_prefix = str(logfolder).removeprefix(str(root_path)).removeprefix("/")
                    insert_statement1 = f"""
                    INSERT INTO robot_logs (log_path, event_name, half, playernumber, headnumber, bodynumber, team1, team2, time) 
                    VALUES ('{logfolder_w_prefix}', '{event.name}', '{halftime}', '{playernumber}', '{head_number}', '{body_number}', '{team1}', '{team2}', to_timestamp('{timestamp}', 'yyyy-mm-dd_hh24-mi-ss'))
                    ON CONFLICT DO NOTHING
                    """
                    cur.execute(insert_statement1)
                    conn.commit()
                # end handling a log
            # end handling a game
    # end handling an event


def insert_experiment_data(db_name):
    for logfile in experiment_list:
        print(logfile)
        event_name = str(logfile).split("/")[0]

        insert_statement1 = f"""
        INSERT INTO {db_name} (log_path, event_name, half) 
        VALUES ('{logfile}', '{event_name}', 'experiment')
        ON CONFLICT DO NOTHING
        """
        cur.execute(insert_statement1)
        conn.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cleanup", action="store_true")
    args = parser.parse_args() 
    
    if args.cleanup is True:
        # This is just for debug purposes
        cleanup()

    create_log_table("robot_logs")
    insert_log_data()
    # create_log_table("experiment_logs")  # could be used to test stuff in a separate table 
    insert_experiment_data("robot_logs")
