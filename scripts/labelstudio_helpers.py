"""
    Set of functions that are occasionally used manually or for testing
"""
from label_studio_sdk import Client
import json

LABEL_STUDIO_URL = "https://ls.berlinunited-cloud.de/"
API_KEY = "6cb437fb6daf7deb1694670a6f00120112535687"
ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
ls.check_connection()

def delete_all_projects():
    existing_projects = ls.list_projects()
    for project in existing_projects:
        project.delete_all_tasks()
        ls.delete_project(project.id)


def create_labelstudio_user():
    print(ls.get_users())
    # ls.create_user({'username':'label_bot', 'email':'bot@berlinunited.com', 'first_name':'eliza', 'last_name':'bot'}, exist_ok=True)

def annotation_backup():
    my_project = ls.get_project(184)
    print(my_project.id)
    snapshot = my_project.export_snapshot_create("my_snapshot")
    print(my_project.export_snapshot_list())

def import_annotation():
    # TODO load the json file
    with open("project-184-at-2024-03-29-11-35-2fd011f6.json") as f:
        annotation_backup = json.load(f)

    for tasks in annotation_backup:
        print(tasks["id"])
        task_id = tasks["id"]
        project_id = tasks["project"]
        my_project = ls.get_project(project_id)
        for annotation in tasks["annotations"]:
            annotation.pop('id', None)
            annotation.pop('unique_id', None)
            print(type(annotation))
            if "result" in annotation:
                for single_result in annotation["result"]:
                    single_result.pop('id', None)
            print(annotation)
            a = my_project.create_annotation(task_id, **annotation)

        

if __name__ == "__main__":
    pass
    #annotation_backup()
    #my_project = ls.get_project(184)
    #my_project.export_snapshot_download(1)
    #my_project.export_snapshot_list()
    #import_annotation()