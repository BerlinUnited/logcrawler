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

def create_tables():
    # log_path is the unique identifier of the row
    sql_query1 = f"""
    CREATE TABLE IF NOT EXISTS  behavior_options (
        log_id INTEGER NOT NULL,
        id INTEGER NOT NULL,
        name VARCHAR NOT NULL,
        PRIMARY KEY (log_id, id),
        CONSTRAINT behavior_options_unique_log_id_id UNIQUE (log_id, id)
    );
    """
    cur.execute(sql_query1)
    conn.commit()
    sql_query2 = f"""
    CREATE TABLE IF NOT EXISTS behavior_options_states (
        log_id INTEGER NOT NULL,
        options_id INTEGER NOT NULL,
        id INTEGER NOT NULL,
        name VARCHAR NOT NULL,
        target BOOLEAN,
        PRIMARY KEY (log_id, options_id, id),
        FOREIGN KEY (log_id, options_id) REFERENCES behavior_options (log_id, id) ON DELETE CASCADE ON UPDATE NO ACTION,
        CONSTRAINT behavior_options_states_constraint UNIQUE (log_id, options_id, id)
    );
    """
    cur.execute(sql_query2)
    conn.commit()
    sql_query3 = f"""
    CREATE TABLE IF NOT EXISTS  behaviorframe_options (
        log_id INTEGER NOT NULL,
        frame INTEGER NOT NULL,
        time INTEGER NOT NULL,
        parent INTEGER NOT NULL,
        id INTEGER NOT NULL,
        timeOfExecution INTEGER NOT NULL,
        activeState INTEGER NOT NULL,
        stateTime INTEGER NOT NULL,
        PRIMARY KEY (log_id, frame, time, parent, id),
        FOREIGN KEY (log_id, id) REFERENCES behavior_options (log_id, id) ON DELETE CASCADE ON UPDATE NO ACTION,
        FOREIGN KEY (log_id, id, activeState) REFERENCES behavior_options_states (log_id, options_id, id) ON DELETE CASCADE ON UPDATE NO ACTION
    );
    """
    cur.execute(sql_query3)
    conn.commit()

def cleanup():
    cur.execute("DROP TABLE IF EXISTS behavior_options, behaviorframe_options, behavior_options_states CASCADE")

def parse_sparse_option(log_id, frame, time, parent, node):
    insert_statement1 = f"""
    INSERT INTO behaviorframe_options VALUES ('{log_id}', '{frame}', '{time}', '{parent}', '{node.option.id}', '{node.option.timeOfExecution}', '{node.option.activeState}', '{node.option.stateTime}') ON CONFLICT DO NOTHING
    """
    cur.execute(insert_statement1)
    conn.commit()
    # TODO add inserting of params here

    # iterating through sub-options
    for sub in node.option.activeSubActions:
        if sub.type == 0: # Option
            parse_sparse_option(log_id, frame, time, node.option.id, sub)
        elif sub.type == 2: # SymbolAssignement
            # NOTE: i doesn't see any benefit in saving the SymbolAssignement; the resulting value is already in the 'outputsymbols'
            pass
        else:
            # NOTE: at the moment i didn't saw any other type ?!
            print(sub)

cleanup()
create_tables()
game_logs = ["/home/stella/robocup/TestLogs/2024-04-19_10-15-00_Berlin United_vs_Dutch Nao Team_half1-after-timeout/3_25_Nao0006_240419-0842/game.log"]

for log_num, game_log in enumerate(game_logs):
    count = 0
    with LogReader(str(game_log)) as gamelog_reader:
        for frame in gamelog_reader.read():
            count += 1
            a = frame["FrameInfo"]
            fn = a.frameNumber

            if "BehaviorStateComplete" in frame:
                print("BehaviorStateComplete")
                full_behavior = frame["BehaviorStateComplete"]
                #proto = Messages_pb2.BehaviorStateComplete()
                #proto.Parse(full_behavior)
                #print(full_behavior)
                
                for i, enum in enumerate(full_behavior.enumerations):
                    #for item in enum.elements:
                    #    self.sql_queue.put(("INSERT INTO behavior_enumerations VALUES (?,?,?,?,?)", [log_num, i, enum.name, item.value, item.name]))
                    pass
                
                for i, option in enumerate(full_behavior.options):
                    # sqlite self.sql_queue.put(("INSERT INTO behavior_options VALUES (?,?,?)", [log_num, i, option.name]))
                    insert_statement1 = f"""
                    INSERT INTO behavior_options (log_id, id, name) VALUES ('{log_num}', '{i}', '{option.name}') ON CONFLICT DO NOTHING
                    """
                    cur.execute(insert_statement1)
                    
                    for j, state in enumerate(option.states):
                        # sqlite self.sql_queue.put(("INSERT INTO behavior_options_states VALUES (?,?,?,?,?)", [log_num, i, j, state.name, state.target]))
                        insert_statement2 = f"""
                        INSERT INTO behavior_options_states VALUES ('{log_num}', '{i}', '{j}','{state.name}', {state.target}) ON CONFLICT DO NOTHING
                        """
                        cur.execute(insert_statement2)
                    
                    #for j, params in enumerate(option.parameters):
                    #    ptype = [ 'decimal', 'boolean', 'enum', 'unknown' ]
                    #    self.sql_queue.put(("INSERT INTO behavior_options_params VALUES (?,?,?,?,?,?,?,?,?)", [log_num, i, params.id, ptype[params.type], params.name, params.decimalValue, params.boolValue, params.enumValue, params.enumTypeId]))
                    #    insert_statement2 = f"""
                    #    INSERT INTO behavior_options_params VALUES ('{log_num}', '{i}', '{params.id}','{ptype[params.type]} '{params.name}') ON CONFLICT DO NOTHING
                    #    """
                conn.commit()
            if "BehaviorStateSparse" in frame:
                print("BehaviorStateSparse")
                sparse_behavior = frame["BehaviorStateSparse"]

                for root in sparse_behavior.activeRootActions:
                    if root.type != 0: # Option
                        print("Root node must be an option!")
                    else:
                        #parse_sparse_option(entry[0], entry[1], entry[2], 0, root)
                        parse_sparse_option(log_num, fn, 1234, 0, root)

            
            if count > 10:
                break

