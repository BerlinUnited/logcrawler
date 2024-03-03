# Berlin United LogCrawler

## Container
The Dockerfile contains all the python packages that are needed to run all the code related to logs. The image is build by the CI and pushed to our gitlab container registry. This image will be used for all code running inside k8s.


## Code
- Should contain code to build and publish an image what can parse logs, connect to the database and can use minio. 
- This generic image will later be used by all pods that need to deal with logs

Write scripts that can do one thing well:
- find all games from a list of suitable events
  - should add those to the db if not exist already
  - use proper datetime so that we can use them in a query
- find all logs for a game and put them in the db
  - add folder of log to the table
- use each log folder from db and check if logs all already combined, if not combine them
  - use a normal pvc in which we download the logs for combining, then we upload it to repl again, after pod dies the pvc should too.
  - should add a flag to the log table for is_combined e {no, yes, not possible}
- if log is combined or not possible to combine and no representation.json is present
  - get representation and write it to json
  - write it also to the robot_logs table similar to what I already did in the logcrawler
- for each log that contains images export them with meta data
  - TODO: where should I save it?
        -> probably in a pvc that persists, so a minio bucket I guess. This would be needed so that we can annotate per log
        -> if we go this route the script can also create the task/projects in labelstudio
- for each log that contains patches export patches as they were recorded (not sure if this is really necessary)
- generate patches from images
- script that can create dataset from sql query like
    - all top images from robot 96 since 2019
    - TODO: how do we get the annotations in the database?







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