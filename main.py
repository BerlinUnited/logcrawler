"""
"""
from pathlib import Path
import time
import psycopg2

# connect to database
params = {"host": "postgres.postgres","port": 5432,"dbname": "postgres","user": "postgres","password": "123"}
conn = psycopg2.connect(**params)
cur = conn.cursor()

def cleanup():
    # FIXME for easier life we will delete all the data first whenever the pod starts. This prevents double entry. 
    cur.execute("DROP TABLE game, robot_logs")

def create_tables():
    # TODO use postgres date / datetime later
    test = """
    CREATE TABLE IF NOT EXISTS game (
        game_id BIGSERIAL PRIMARY KEY,
        game_name VARCHAR,
        event_name VARCHAR,
        game_date VARCHAR,
        game_time VARCHAR,
        halftime INT,
        team1 VARCHAR,
        team2 VARCHAR
    );

    CREATE TABLE IF NOT EXISTS robot_logs (
        game_id BIGINT REFERENCES game (game_id),
        playernumber INT,
        headnumber INT,
        bodynumber VARCHAR
    );
    """
    cur.execute(test)
    conn.commit()



def get_game_data(event_path):
    """
        function that fills 
    """
    event_name = event_path.name
    for game in event_path.iterdir():
        if game.is_dir():
            print(f"\t{game}")
            # ignore test games
            if "test" in str(game.name).lower(): 
                continue
            # parse additional information from game folder
            game_parsed = str(game.name).split("_")
            date = game_parsed[0]
            time = game_parsed[1]
            team1 = game_parsed[2]
            team2 = game_parsed[4]
            halftime = game_parsed[5][-1]

            # TODO maybe improve insertion like this sql_string = "INSERT INTO domes_hundred (name,name_slug,status) VALUES (%s,%s,%s) RETURNING id;"
            insert_statement = f"""
            INSERT INTO game (game_name, event_name, game_date, game_time, halftime, team1, team2) 
            
            VALUES ('{game.name}', '{event_name}', '{date}', '{time}', '{halftime}', '{team1}', '{team2}')
            RETURNING game_id;
            """
            cur.execute(insert_statement)
            game_id = cur.fetchone()[0]
            conn.commit()
            get_robot_data(game, game_id)
            # TODO video data
            # TODO gamecontroller data

    

    cur.execute("SELECT * FROM game;")
    print(cur.fetchall())

def get_robot_data(game_path, game_id):
    gamelog_path = Path(game_path) / "game_logs"
    for logfolder in gamelog_path.iterdir():
        print(f"\t\t{logfolder}")
        logfolder_parsed = str(logfolder.name).split("_")
        playernumber = logfolder_parsed[0]
        head_number = logfolder_parsed[1]
        body_number = logfolder_parsed[2]
        insert_statement = f"""
        INSERT INTO robot_logs (game_id, playernumber, headnumber, bodynumber) 
        VALUES ('{game_id}', '{playernumber}', '{head_number}', '{body_number}');
        """
        cur.execute(insert_statement)
        conn.commit()

        # TODO actually parse the logs
        


def main_loop():
    """
    Currently we only parse selected events to make our lives easier

    TODO if we select all events we need to have some logic that rejects too old data and folders containing the word experiment and others 
    """
    eventlist = ["2019-05-01_GO19", "2019-03-28_Aspen"]
    d = Path('/mnt/repl/')
    for event in d.iterdir():
        if event.is_dir():
            if event.name in eventlist:
                print(event)
                get_game_data(event)


cleanup()
create_tables()
main_loop()


# we will sleep in the end so that we have time to look at the logs
while True:
    time.sleep(5)