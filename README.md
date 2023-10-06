# Berlin United LogCrawler

TODO

## Possible improvements
- move the k8s yaml from the k8s cluster repo to this repo and use configmaps for the code



"""
"""
import pathlib
import time
import psycopg2

# connect to database
params = {"host": "postgres.postgres","port": 5432,"dbname": "postgres","user": "postgres","password": "123"}
conn = psycopg2.connect(**params)
cur = conn.cursor()

# create schema
# TODO create table if not exist
test = """
CREATE TABLE game (
 id SERIAL PRIMARY KEY,
  game_name VARCHAR,
  event_name VARCHAR
);

CREATE TABLE robot_logs (
  id INT,
  	game_name VARCHAR,
  	robot_id INT
    robot_name VARCHAR

);

creation of log table:
     QUESTION: what are the columnnames???

"""
def get_all_representations():
    load all the json files
    unique_list_representations = set(list of dict)


def populate_game_table(event_name, game_names):
    INSERT INTO game (game_name, event_name) VALUES ('game1', 'cool_event');
    INSERT INTO game (game_name, event_name) VALUES ('game2', 'cool_event');
    INSERT INTO game (game_name, event_name) VALUES ('game3', 'cool_event');
    INSERT INTO game (game_name, event_name) VALUES ('game4', 'cool_event');


def parse_log(logfile):
    for frame in logfile
        parsedframe = parse_frame()
        INSERT INTO logtable (parsedframe.columnames) VALUES (parsedframe.values)


for event in events():
    event_name = parse(event)
    game_names = parse(subfolders(event))
    populate_game_table(event_name, game_names)
    
    for game in game_names():
        get_robot_data()
        get_video_data()

        for robot in game:
            parse_log(logfile)

# insert values
cur.execute(test)
test2 = """


INSERT INTO robot_logs (game_name, robot_id) VALUES ('game1', 94);
INSERT INTO robot_logs (game_name, robot_id) VALUES ('game2', 94);
INSERT INTO robot_logs (game_name, robot_id) VALUES ('game3', 94);
INSERT INTO robot_logs (game_name, robot_id) VALUES ('game4', 94);
INSERT INTO robot_logs (game_name, robot_id) VALUES ('game5', 94);
"""
cur.execute(test2)

query = """
SELECT id FROM game WHERE game_name='game2';
"""
cur.execute(query)
bla = cur.fetchone()
print(bla)

# folder path
dir_path = '/mnt/repl/'
# construct path object
d = pathlib.Path(dir_path)

#-------------------
# Create db logs if not exists
    # or we rename the db

# maybe log into the db

# create table game
# game_name | event_name | date | team1 | team2 | is_test_game | halftime

    # game1 | Gore23
    # game2 | Gore23

# create table video
# videoname | folder

# create table gamecontroller data
# initlog | log |finished_log
    # <path to> | <path to> | <path to >

# create table robot_logs
# 1 to many relationship to table game
# robot_id | git status | 

# TODO find a cool table name
# frame number | image top path |image bottom path | ... | ...