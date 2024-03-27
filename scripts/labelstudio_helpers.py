"""
    Set of function that are occasionally used manually
"""
from label_studio_sdk import Client

LABEL_STUDIO_URL = "https://ls.berlinunited-cloud.de/"
API_KEY = "6cb437fb6daf7deb1694670a6f00120112535687"
ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()

def delete_all_projects():
    existing_projects = ls.list_projects()
    for project in existing_projects:
        project.delete_all_tasks()
        ls.delete_project(project.id)

delete_all_projects()