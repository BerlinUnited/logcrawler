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
        game_id SERIAL PRIMARY KEY,
        game_name VARCHAR,
        event_name VARCHAR,
        game_date VARCHAR,
        game_time VARCHAR,
        halftime INT,
        team1 VARCHAR,
        team2 VARCHAR
    );

    CREATE TABLE IF NOT EXISTS robot_logs (
        game_id INT,
        game_name VARCHAR,
        robot_id INT,
        robot_name VARCHAR
    );
    """
    # TODO add fields for playernumber, headnumber, bodynumber
    # TODO change id to game_id
    # TODO think about foreign keys here?
    cur.execute(test)
    conn.commit()


    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
    table_names = cur.fetchall()
    print(f"created tables: {table_names}")


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
      
            insert_statement = f"""
            INSERT INTO game (game_name, event_name, game_date, game_time, halftime, team1, team2) 
            
            VALUES ('{game.name}', '{event_name}', '{date}', '{time}', '{halftime}', '{team1}', '{team2}');
            """
            cur.execute(insert_statement)
            conn.commit()
            # TODO get id from inserted row


            #get_robot_data(game_id)

    

    cur.execute("SELECT * FROM game;")
    print(cur.fetchall())

def get_robot_data():
    pass

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