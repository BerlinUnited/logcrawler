"""
    Some examples showing you how to work with the postgres data
"""
import random
import string
import psycopg2
from datetime import datetime
from os import environ

params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get('DB_PASS'),
}
conn = psycopg2.connect(**params)
cur = conn.cursor()


def dummy_query():
    select_statement1 = f"""
    SELECT playernumber FROM robot_logs where time between '2019-04-04' and '2023-07-07' AND headnumber = 93
    """
    cur.execute(select_statement1)
    rtn_val = cur.fetchall()
    print(rtn_val)


def datetime_test_setup():
    sql_query = """
    CREATE TABLE IF NOT EXISTS dummy_table (
        string VARCHAR, 
        time timestamp
    );
    """
    cur.execute(sql_query)
    conn.commit()

def datetime_test(log_time):
    cool_string = ''.join(random.choices(string.ascii_lowercase, k=22))

    insert_statement = f"""
    INSERT INTO dummy_table (string, time) VALUES ('{cool_string}', to_timestamp('{log_time}', 'yyyy-mm-dd_hh24-mi-ss'));
    """
    cur.execute(insert_statement)
    conn.commit()


def query_test():
    select_statement = f"""
    SELECT log_path FROM robot_logs WHERE date_part('hour',CAST(time AS timestamp)) > 12;
    """
    cur.execute(select_statement)
    rtn_val = cur.fetchall()
    print(rtn_val)


def add_column():
    sql_statement = f"""
    ALTER TABLE robot_logs ADD broken_images VARCHAR;
    """
    cur.execute(sql_statement)
    conn.commit()


def set_broken_images(bucket_id):
    """
    useful when we notice during training that all images are scrambled (we have a few of those)
    FIXME: implement this
    """
    pass


if __name__ == "__main__":
    pass
