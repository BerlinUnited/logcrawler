import psycopg2
from os import environ
from naoth.log import Reader as LogReader
from naoth.log import Parser

from naoth.pb import Messages_pb2

# connect to database
params = {
    "host": "pg.berlin-united.com",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get("DB_PASS"),
}
conn = psycopg2.connect(**params)
cur = conn.cursor()


insert_statement1 = f"""
    CREATE VIEW behaviorframe_options_v AS
    SELECT f.log_id, f.frame, f.time, f.parent, f.id, o.name, f.timeOfExecution, f.activeState, s.name as stateName, s.target, f.stateTime
    FROM behaviorframe_options AS f
    inner join behavior_options o on o.log_id = f.log_id and o.id = f.id
    inner join behavior_options_states s on s.log_id = f.log_id and s.options_id = f.id and s.id = f.activeState
    """
cur.execute(insert_statement1)
conn.commit()