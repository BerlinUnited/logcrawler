# Berlin United LogCrawler

TODO

## Possible improvements
For creating another db have a look at this: https://stackoverflow.com/questions/74899785/psycopg2-errors-activesqltransaction-create-database-cannot-run-inside-a-transa


---
# create schema


creation of log table:
     QUESTION: what are the columnnames???

"""
def get_all_representations():
    load all the json files
    unique_list_representations = set(list of dict)



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