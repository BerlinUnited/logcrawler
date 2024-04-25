"""
    Mark a project as labeled
"""
from label_studio_sdk import Client
import json
import psycopg2
from os import environ
import requests
from time import sleep

ls = Client(url=environ.get('LS_URL'), api_key=environ.get('LS_KEY'))
ls.check_connection()

params = {
    "host": "pg.berlinunited-cloud.de",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get('DB_PASS'),
}
conn = psycopg2.connect(**params)
cur = conn.cursor()

def hex_to_rgb(value):
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def mark_project_done(project_id):
    """
    this is only needed once to color everything that is already validated - use this if we want to change colors
    """
    print(project_id)
    # Find out if the project is bottom or top
    top_base_color = "#D55C9D"  # pink
    bottom_base_color = "#51AAFD"  # blue

    select_statement1 = f"""
    SELECT exists (SELECT 1 FROM robot_logs WHERE ls_project_bottom = '{project_id}' LIMIT 1);
    """
    cur.execute(select_statement1)
    rtn_val = cur.fetchall()[0][0]
    if rtn_val:
        # is_bottom = True
        select_statement1 = f"""
        SELECT bottom_validated FROM robot_logs where ls_project_bottom = '{project_id}'
        """
        cur.execute(select_statement1)
        output = cur.fetchall()
        print(f"\t{output}")
        validated = output[0][0]

        if validated:
            project = ls.get_project(project_id)
            r, g, b = hex_to_rgb(bottom_base_color)
            project.set_params(**{"color": f"{bottom_base_color}&linear-gradient(90deg, rgba({r}, {g}, {b},0.7) 0%, rgba(253,187,45,0.7) 100%)"})
    else:
        # is_bottom = False
        print(f"\ttop")
        select_statement1 = f"""
        SELECT top_validated FROM robot_logs where ls_project_top = '{project_id}'
        """
        cur.execute(select_statement1)
        output = cur.fetchall()
        print(f"\t{output}")
        validated = output[0][0]

        if validated:
            project = ls.get_project(project_id)
            r, g, b = hex_to_rgb(top_base_color)
            project.set_params(**{"color": f"{top_base_color}&linear-gradient(90deg, rgba({r}, {g}, {b},0.7) 0%, rgba(253,187,45,0.7) 100%)"})

def mark_project_done2(project_id):
    """
    
    """
    print(project_id)
    # Find out if the project is bottom or top
    top_base_color = "#D55C9D"  # pink
    bottom_base_color = "#51AAFD"  # blue

    select_statement1 = f"""
    SELECT exists (SELECT 1 FROM robot_logs WHERE ls_project_bottom = '{project_id}' LIMIT 1);
    """
    cur.execute(select_statement1)
    rtn_val = cur.fetchall()[0][0]
    if rtn_val:
        # is_bottom = True
        select_statement1 = f"""
        UPDATE robot_logs SET bottom_validated = true
        """
        project = ls.get_project(project_id)
        r, g, b = hex_to_rgb(bottom_base_color)
        project.set_params(**{"color": f"{bottom_base_color}&linear-gradient(90deg, rgba({r}, {g}, {b},0.7) 0%, rgba(253,187,45,0.7) 100%)"})
    else:
        #is_bottom = False
        select_statement1 = f"""
        UPDATE robot_logs SET top_validated = true
        """
        project = ls.get_project(project_id)
        r, g, b = hex_to_rgb(top_base_color)
        project.set_params(**{"color": f"{top_base_color}&linear-gradient(90deg, rgba({r}, {g}, {b},0.7) 0%, rgba(253,187,45,0.7) 100%)"})

if __name__ == "__main__":
    mark_project_done2(120)

    
