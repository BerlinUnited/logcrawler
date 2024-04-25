"""
    Set of functions that are occasionally used manually or for testing
"""
from label_studio_sdk import Client
import json
from os import environ
import requests
from time import sleep

ls = Client(url=environ.get('LS_URL'), api_key=environ.get('LS_KEY'))
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

def update_label_config():
    my_project = ls.get_project(351)
    new_label_config_bb = """
    <View>
    <Image name="image" value="$image"/>
    <RectangleLabels name="label" toName="image">
        <Label value="ball" background="#9eaeff"/>
        <Label value="nao" background="#D4380D"/>
        <Label value="penalty_mark" background="#e109da"/>
        <Label value="referee" background="#000000"/>
    </RectangleLabels>
    <Number name="blurry" toName="image" />
    </View>
    """
    my_json = {"title": "blub", "label_config": new_label_config_bb}
    my_project.set_params(**my_json)

def sync_storage(project_id):
    my_project = ls.get_project(project_id)
    a = my_project.get_import_storages()
    storage_id = a[0]["id"]

    url = f'https://ls.berlinunited-cloud.de/api/storages/s3/{storage_id}/sync'
    
    while True:
        try:
            # TODO I could get the status first and then abort before trying to sync?
            x = requests.post(url, headers={"Authorization": "Token 6cb437fb6daf7deb1694670a6f00120112535687"})
            print(x.json()["status"])
            if x.json()["status"] == "completed":
                break
            else:
                sleep(1)
        except requests.exceptions.ReadTimeout: 
            sleep(1)
    

if __name__ == "__main__":
    pass
    #annotation_backup()
    #my_project = ls.get_project(184)
    #my_project.export_snapshot_download(1)
    #my_project.export_snapshot_list()
    #import_annotation()
    #update_label_config()
    sync_storage(359)