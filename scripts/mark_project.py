"""
Mark a project as labeled by applying a color gradient in label studio 
and updating the database to reflect the validation status.
"""
import argparse
from os import environ

import psycopg2
from label_studio_sdk import Client

ls = Client(url=environ.get("LS_URL"), api_key=environ.get("LS_KEY"))
ls.check_connection()

params = {
    "host": "pg.berlin-united.com",
    "port": 4000,
    "dbname": "logs",
    "user": "naoth",
    "password": environ.get("DB_PASS"),
}
conn = psycopg2.connect(**params)
cur = conn.cursor()


TOP_BASE_COLOR = "#D55C9D"  # pink
BOTTOM_BASE_COLOR = "#51AAFD"  # blue


def hex_to_rgb(value):
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


def check_if_is_bottom(project_id):
    top_or_bottom_select_statement = f"""
    SELECT exists (SELECT 1 FROM robot_logs WHERE ls_project_bottom = '{project_id}' LIMIT 1);
    """
    cur.execute(top_or_bottom_select_statement)
    is_bottom = cur.fetchall()[0][0]

    return is_bottom


def validated_color_from(base_color):
    r, g, b = hex_to_rgb(base_color)
    return f"{base_color}&linear-gradient(90deg, rgba({r}, {g}, {b},0.7) 0%, rgba(253,187,45,0.7) 100%)"


def set_ls_project_color(project_id, color):
    project = ls.get_project(project_id)
    project.set_params(**{"color": color})


def db_mark_top_validated(project_id, validated=True):
    validated_sql = "true" if validated else "NULL"

    update_statement = f"""
    UPDATE robot_logs
    SET top_validated = {validated_sql}
    WHERE ls_project_top = '{project_id}';
    """
    cur.execute(update_statement)
    assert cur.rowcount == 1, "Aborting, updated more than one row."
    conn.commit()


def db_mark_bottom_validated(project_id, validated=True):
    validated_sql = "true" if validated else "NULL"

    update_statement = f"""
    UPDATE robot_logs
    SET bottom_validated = {validated_sql}
    WHERE ls_project_bottom = '{project_id}';
    """
    cur.execute(update_statement)
    assert cur.rowcount == 1, "Aborting, updated more than one row."
    conn.commit()


def mark_project_done(project_id, mark_validated_db=True):
    """
    This function colors a project in label studio as done by applying a gradient color
    to the project. By default, it will also mark the project as validated in the DB.
    """
    print(f"Marking {project_id} as done")

    # Find out if the project is bottom or top
    is_bottom = check_if_is_bottom(project_id)

    if is_bottom:
        if mark_validated_db:
            db_mark_bottom_validated(project_id)

        set_ls_project_color(project_id, color=validated_color_from(BOTTOM_BASE_COLOR))

    else:
        # is top
        if mark_validated_db:
            db_mark_top_validated(project_id)

        set_ls_project_color(project_id, color=validated_color_from(TOP_BASE_COLOR))


def mark_project_not_done(project_id, mark_validated_db=True):
    """
    This function colors a project in label studio as not by applying a solid color
    to the project. By default, it will  mark the project as not validated in the DB.
    """
    print(f"Marking {project_id} as done")

    # Find out if the project is bottom or top
    is_bottom = check_if_is_bottom(project_id)

    if is_bottom:
        if mark_validated_db:
            db_mark_bottom_validated(project_id, validated=False)

        set_ls_project_color(project_id, color=BOTTOM_BASE_COLOR)

    else:
        # is top
        if mark_validated_db:
            db_mark_top_validated(project_id, validated=False)

        set_ls_project_color(project_id, color=TOP_BASE_COLOR)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--project",
        nargs="+",
        required=True,
        type=int,
        help="Labelstudio project ids separated by a space",
    )

    parser.add_argument(
        "-u",
        "--undo",
        action="store_true",
        required=False,
        help="If set it will mark the given projects as not done",
    )

    args = parser.parse_args()
    projects = args.project
    for prj in projects:
        if args.undo:
            mark_project_not_done(prj)
        else:
            mark_project_done(prj)
