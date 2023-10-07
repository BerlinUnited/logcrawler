"""
"""
from pathlib import Path
import time
import psycopg2
from naoth.log import Parser
from naoth.log import Reader as LogReader
from naoth.pb.Framework_Representations_pb2 import Image

# connect to database
params = {"host": "postgres.postgres","port": 5432,"dbname": "postgres","user": "postgres","password": "123"}
conn = psycopg2.connect(**params)
cur = conn.cursor()

def cleanup():
    # FIXME for easier life we will delete all the data first whenever the pod starts. This prevents double entry. 
    cur.execute("DROP TABLE game, robot_logs")


def create_tables_step1():
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

    CREATE TABLE IF NOT EXISTS representations (
        representation_name VARCHAR,
        CONSTRAINT rep_constraint UNIQUE (representation_name)
    );
    """
    cur.execute(test)
    conn.commit()


def create_tables_step2():
    cur.execute("SELECT * FROM representations")
    rtn_val = cur.fetchall()

    # we get list of tuples each tuple represents one row
    # combine it with the string VARCHAR so that we can create a valid SQL query out of it
    rep_list = [str(row[0]) + " VARCHAR" for row in rtn_val]

    create_table_query = """CREATE TABLE IF NOT EXISTS log ({0});""".format(', '.join( rep_list ))

    cur.execute(create_table_query)
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

        # actually parse the logs
        parse_log_data(logfolder)


def parse_log_data(logfolder):
    gamelog = logfolder / "game.log"
    print(f"parsing {gamelog}")
    my_parser = Parser()
    log = LogReader(gamelog, my_parser)
    # TODO think about how to actually insert
    for i, frame in enumerate(log):
        print("\tframe: ", i)
        dict_keys = frame.get_names()
        for key in dict_keys:
            print(frame[key])
            # we cant just insert frame[key] because all the keys belong to the same insert command otherwise they would go on different rows
        break

    # TODO parse the image log


def export_representations_from_log(event_path):
    """
        Idea is to find all representations put that into db table, later on we will use this table to create the logs table
    """
    for game in sorted(event_path.iterdir()):
        game_log_folder = Path(game) / "game_logs"

        for robot in sorted(game_log_folder.iterdir()):
            # TODO add images.log representations
            print(f"\t{robot}")
            gamelog = robot / "game.log"
            img_log = robot / "images.log"

            my_parser = Parser()

            log = LogReader(gamelog, my_parser)
            for i, frame in enumerate(log):
                dict_keys = frame.get_names()
                for key in dict_keys:
                    insert_statement = f"""
                    INSERT INTO representations (representation_name) 
                    VALUES ('{key}') ON CONFLICT DO NOTHING;
                    """
                    cur.execute(insert_statement)
                # only check the first few frames
                if i > 20:
                    break

            conn.commit()

        break
    return


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

def prep_loop():
    """
        this is something that needs to run continuously and it should fix or identify problems in the structure of the data
    """
    eventlist = ["2019-05-01_GO19", "2019-03-28_Aspen"]
    d = Path('/mnt/repl/')
    print("running prep loop")
    for event in d.iterdir():
        if event.is_dir():
            if event.name in eventlist:
                export_representations_from_log(event)
    print("finished prep loop")

cleanup()
create_tables_step1()
prep_loop()
create_tables_step2()
# TODO create tables step 2 (table for actual parsed log data)

main_loop()


# we will sleep in the end so that we have time to look at the logs
while True:
    time.sleep(5)