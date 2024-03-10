import psycopg2

# connect to database
# TODO: set up ingress so that i can test locally
params = {"host": "pg.berlinunited-cloud.de","port": 4000,"dbname": "logs","user": "naoth","password": "fsdjhwzuertuqg"}
conn = psycopg2.connect(**params)
cur = conn.cursor()

def cleanup():
    # FIXME for easier life we will delete all the data first whenever the pod starts. This prevents double entry. 
    cur.execute("DROP TABLE robot_logs")

def create_log_table():
    # TODO use postgres date / datetime later
    # TODO add event name
    sql_query = """
    CREATE TABLE IF NOT EXISTS robot_logs (
        game_name VARCHAR,
        playernumber INT,
        headnumber INT,
        bodynumber VARCHAR,
        team1 VARCHAR,
        team2 VARCHAR,
        day DATE
    );
    """
    cur.execute(sql_query)
    conn.commit()

def dummy_insert():
    insert_statement1 = f"""
    INSERT INTO robot_logs (game_name, playernumber, headnumber, bodynumber, team1, team2, day) 
    
    VALUES ('testgame', 1, 45, 'bodynumber1', 'team1', 'team2', '2023-07-08')
    """
    cur.execute(insert_statement1)
    insert_statement2 = f"""
    INSERT INTO robot_logs (game_name, playernumber, headnumber, bodynumber, team1, team2, day) 
    
    VALUES ('testgame2', 2, 55, 'bodynumber2', 'team1', 'team2', '2023-07-06')
    """
    cur.execute(insert_statement2)
def dummy_query():
    select_statement1 = f"""
    SELECT * FROM robot_logs where day between '2023-07-05' and '2023-07-08'
    """
    cur.execute(select_statement1)
    rtn_val = cur.fetchall()
    print(rtn_val)

cleanup()
create_log_table()
dummy_insert()
dummy_query()

