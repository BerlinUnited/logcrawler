import psycopg2
from pathlib import Path
from os import environ
from event_list import event_list

# connect to database
params = {"host": "pg.berlinunited-cloud.de","port": 4000,"dbname": "logs","user": "naoth","password": "fsdjhwzuertuqg"}
conn = psycopg2.connect(**params)
cur = conn.cursor()

def cleanup():
    # FIXME for easier life we will delete all the data first whenever the pod starts. This prevents double entry. 
    cur.execute("DROP TABLE robot_logs")

def create_log_table():
    # TODO use postgres date / datetime later with actual time of game 
    # log_path is the unique identifier of the row
    sql_query = """
    CREATE TABLE IF NOT EXISTS robot_logs (
        log_path VARCHAR, 
        event_name VARCHAR,
        half VARCHAR,
        playernumber INT,
        headnumber INT,
        bodynumber VARCHAR,
        team1 VARCHAR,
        team2 VARCHAR,
        time DATE,
        broken BOOLEAN DEFAULT FALSE,
        representation_exists BOOLEAN,
        images_exist BOOLEAN,
        combined_status BOOLEAN,
        extract_status BOOLEAN,
        minio_bucket VARCHAR,
        labelstudio_project VARCHAR, 
        CONSTRAINT my_constraint UNIQUE (log_path)
    );
    """
    cur.execute(sql_query)
    conn.commit()

def insert_data():
    # FIXME '/mnt/q/' is specific to my windows setup - make sure it works on other machines as well
    root_path = environ.get('LOG_ROOT') or '/mnt/q/'  # use or with environment variable to make sure it works in k8s as well
    for event in [f for f in Path(root_path).iterdir() if f.is_dir()]:
        if event.name in event_list:
            print(event)
            event_name = event.name
            for game in [f for f in event.iterdir() if f.is_dir()]:
                print(f"\t{game}")
                # ignore test games - FIXME (i should not do that but I have to make sure testgames are in correct format before)
                if "test" in str(game.name).lower(): 
                    continue
                # for now we allow only on folder called Experiments to also exist inside the Event folder -> TODO have discussion about additional folders
                if str(game.name) == "Experiments":
                    continue
                # parse additional information from game folder
                game_parsed = str(game.name).split("_")
                date = game_parsed[0]
                time = game_parsed[1]
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
                    VALUES ('{logfolder_w_prefix}', '{event.name}', '{halftime}', '{playernumber}', '{head_number}', '{body_number}', '{team1}', '{team2}', '{date}')
                    ON CONFLICT DO NOTHING
                    """
                    cur.execute(insert_statement1)
                    conn.commit()
                # end handling a log
            # end handling a game
    # end handling an event

if __name__ == "__main__":
    cleanup()  # This is just for debug purposes use if not exists and unique constraints in the end to make sure to not have any duplicates
    create_log_table()
    insert_data()
