"""
    Set of functions that are occasionally used manually or for testing
"""

from label_studio_sdk import Client
import json
from os import environ
import requests
from time import sleep
import uuid
from tqdm import tqdm

ls = Client(url=environ.get("LS_URL"), api_key=environ.get("LS_KEY"))
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
            annotation.pop("id", None)
            annotation.pop("unique_id", None)
            print(type(annotation))
            if "result" in annotation:
                for single_result in annotation["result"]:
                    single_result.pop("id", None)
            print(annotation)
            a = my_project.create_annotation(task_id, **annotation)


def update_label_config():
    new_label_config_bb = """
    <View>
    <Image name="image" value="$image"/>
    <RectangleLabels name="label" toName="image">
        <Label value="ball" background="#9eaeff"/>
        <Label value="nao" background="#D4380D"/>
        <Label value="penalty_mark" background="#e109da"/>
        <Label value="referee" background="#000000"/>
    </RectangleLabels>
    <Relations>
        <Relation value="in front of" />
    </Relations>
    </View>
    """
    existing_projects = ls.list_projects()
    for project in existing_projects:
        print(project.id)
        my_project = ls.get_project(project.id)
        my_json = {"label_config": new_label_config_bb}
        my_project.set_params(**my_json)


def sync_storage(project_id):
    my_project = ls.get_project(project_id)
    a = my_project.get_import_storages()
    storage_id = a[0]["id"]

    url = f"https://ls.berlin-united.com/api/storages/s3/{storage_id}/sync"

    while True:
        try:
            # TODO I could get the status first and then abort before trying to sync?
            x = requests.post(
                url,
                headers={
                    "Authorization": "Token 6cb437fb6daf7deb1694670a6f00120112535687"
                },
            )
            print(x.json()["status"])
            if x.json()["status"] == "completed":
                break
            else:
                sleep(1)
        except requests.exceptions.ReadTimeout:
            sleep(1)


def update_all_storage_endpoint():
    existing_projects = ls.list_projects()
    for project in existing_projects:
        print(project.id)
        my_project = ls.get_project(project.id)
        a = my_project.get_import_storages()
        storage_id = a[0]["id"]

        url = f"https://ls.berlin-united.com/api/storages/s3/{storage_id}"

        x = requests.patch(
                    url,
                    headers={
                        "Authorization": "Token 6cb437fb6daf7deb1694670a6f00120112535687"
                    },
                    data={"s3_endpoint": "https://minio.berlin-united.com"}
                )
        print(f"\t{x.json()}")


def get_single_annotation():
    my_project = ls.get_project(140)
    print(my_project.get_annotation(12512))


def validate_project_verification():
    pass

    
def create_dummy_annotation():
    single_ls_result = [{'type': 'rectanglelabels', 
                        'value': {'x': 20, 'y': 20, 'width': 10, 'height': 10,'rotation': 0, 'rectanglelabels': ["ball"]}, 
                        'to_name': 'image', 'from_name': 'label','origin': 'manual', 'original_width': 640, 
                        'original_height': 480},
                        {'type': 'rectanglelabels', 
                        'value': {'x': 40, 'y': 40, 'width': 10, 'height': 10,'rotation': 0, 'rectanglelabels': ["ball"]}, 
                        'to_name': 'image', 'from_name': 'label','origin': 'manual', 'original_width': 640, 
                        'original_height': 480}]
    ls_result = {"result": single_ls_result, 'completed_by': 2}

    my_project = ls.get_project(639)
    a = my_project.create_annotation(212076, **ls_result)
    print(a)

def print_task(project, task):
    project = ls.get_project(project)
    task = project.get_task(16130)
    print(task)
    

def add_missing_result_ids():
    """
    get all tasks that have annotations and add an id to it if it not already exists
    A problem exists where the relations know about the existing id's but the bounding boxes do not. What happens when renaming the id?

    ATTENTION: this requires that there is only one annotation per task see function find_multiple_annotations for making sure that it is
    """
    projects = ls.get_projects()
    for project in projects:
        print(project.id)
        labeled_tasks = project.get_labeled_tasks()
        for task in tqdm(labeled_tasks):
            annotations = task["annotations"]
            for annotation in annotations:
                has_relation = False
                for result in annotation["result"]:
                    if result["type"] == "relation":
                        has_relation = True
                if not has_relation:
                    # if we don't have any relation to take care of we delete the annotation and recreate it with results that have id's
                    
                    missing_at_least_one_id = False
                    for result in annotation["result"]:
                        if result["type"] == "rectanglelabels":
                            if not "id" in result:
                                missing_at_least_one_id = True

                    if missing_at_least_one_id:
                        new_results = list()
                        for result in annotation["result"]:
                            if result["type"] == "rectanglelabels":
                                single_ls_result = result
                                if not "id" in single_ls_result:
                                    single_ls_result["id"] = uuid.uuid4().hex[:9].upper()
                                new_results.append(single_ls_result)
                        ls_result = {"result": new_results, 'completed_by': 2}
                        project.delete_annotation(annotation["id"])
                        a = project.create_annotation(task["id"], **ls_result)
                        #print(task["id"], end="\r")


def fix_multiple_annotations():
    """
    get all tasks that have annotations and add an id to it if it not already exists
    A problem exists where the relations know about the existing id's but the bounding boxes do not. What happens when renaming the id?
    """
    def get_project_url_from_task(task: dict):
        project_id = task["project"]
        task_id = task["id"]
        return f"{environ.get('LS_URL')}projects/{project_id}/data?task={task_id}"

    projects = ls.get_projects()
    projects = [ls.get_project(599),ls.get_project(610),ls.get_project(605),ls.get_project(601),ls.get_project(600)]
    for project in projects:
        print(project.id)
        labeled_tasks = project.get_labeled_tasks()
        for task in labeled_tasks:
            if len(task["annotations"]) > 1:
                for annotation in task["annotations"]:
                    # TODO I could also write a merge function here but then I could have duplicate bounding boxes
                    # This should always be verified first
                    # 2 is the id of the bot user
                    if annotation["completed_by"] == 2:
                        project.delete_annotation(annotation["id"])


if __name__ == "__main__":
    pass
    #create_dummy_annotation()
    #print_task(109, 16318)
    add_missing_result_ids()
    #fix_multiple_annotations()