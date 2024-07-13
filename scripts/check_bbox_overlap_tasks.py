from dataclasses import dataclass
from label_studio_sdk import Client
from tqdm import tqdm
import os, sys

helper_path = os.path.join(os.path.dirname(__file__), '../patch_exporter')
sys.path.append(helper_path)
from helper import BoundingBox, Point2D

LABEL_STUDIO_URL = "https://ls.berlin-united.com/"
API_KEY = "6cb437fb6daf7deb1694670a6f00120112535687"

@dataclass
class Annotation:
    label: str
    bbox: BoundingBox

@dataclass
class Overlap:
    a1: Annotation
    a2: Annotation


def get_annotations_from_task(task: dict):
    annotations = task["annotations"]

    annotation_objs = []
    duplicate_annotation = []
    missing_ids = False

    if len(task["annotations"]) > 1:
        duplicate_annotation.append(get_project_url_from_task(task))

    for annotation in annotations:
        # collect all the relations first
        for result in annotation["result"]:
            if result["type"] != "relation":
                # PROBLEM: relations work between id's of results, not all results of type rectanglelabels have idÄs
                continue

        for result in annotation["result"]:
            
            if result["type"] != "rectanglelabels":
                continue

            label = result["value"]["rectanglelabels"][0]
            bbox = bbox_from_result(result)

            annotation_obj = Annotation(label, bbox) 
            annotation_objs.append(annotation_obj)

            if not "id" in result:
                missing_ids = True

    # return missing id true if one result does not have the id key
    return annotation_objs, missing_ids, duplicate_annotation

def bbox_from_result(result: dict):
    x = result["value"]["x"]
    y = result["value"]["y"]
    width = result["value"]["width"]
    height = result["value"]["height"]
    return BoundingBox(Point2D(x, y), Point2D(x + width, y + height))

def get_overlapping_boxes(annotations: list[Annotation]):
    overlapping_boxes = []
    discarded_boxes = []

    for i, a1 in enumerate(annotations):
        for j, a2 in enumerate(annotations):
            if i == j:
                continue
            
            overlap_box = a1.bbox.intersection(a2.bbox)
            if overlap_box is not None:
                overlap = Overlap(a1, a2)
                # guessed value - we need to check if this is a good value
                if overlap_box.area < 100:
                    discarded_boxes.append(overlap)
                else:
                    # TODO check if we already set a relation
                    overlapping_boxes.append(overlap)

    return overlapping_boxes, discarded_boxes

def get_all_labeled_tasks(ls: Client):
    print("Fetching all projects...")
    projects = ls.get_projects()

    print(f"Fetching all labeled tasks from {len(projects)} projects...")
    for project in projects:
        labeled_tasks = project.get_labeled_tasks()
        for tasks in labeled_tasks:
            yield tasks
    #return labeled_tasks

def get_project_url_from_task(task: dict):
    project_id = task["project"]
    task_id = task["id"]
    return f"{LABEL_STUDIO_URL}projects/{project_id}/data?task={task_id}"

if __name__ == "__main__":
    ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
    ls.check_connection()

    labled_tasks = get_all_labeled_tasks(ls)

    tasks_with_overlap = []
    tasks_with_overlap2 = []
    tasks_with_missing_ids = []

    for task in (pbar := tqdm(labled_tasks)):
        pbar.set_description(f"Checking task {task['id']}")
        task_url = get_project_url_from_task(task)
        try: 
            annotations, missing_ids, duplicate_annotation = get_annotations_from_task(task)
        except:
            print("could not get annotations from task")
            quit()

        if missing_ids:
            tasks_with_missing_ids.append(task_url)

        try:
            overlapping_boxes, discard_boxes = get_overlapping_boxes(annotations) 
            # we are only interested in overlapping boxes with different labels
            # e.g. ball and nao, or penalty_mark and ball
            for overlap in overlapping_boxes:
                if overlap.a1.label != overlap.a2.label:
                    tasks_with_overlap.append(task_url)
            
            for overlap in discard_boxes:
                if overlap.a1.label != overlap.a2.label:
                    tasks_with_overlap2.append(task_url)
        except Exception as e:
            print(f"Error while checking task {task['id']} for project {task['project']}: {e}")
            print(task)
            quit()
        
    
    tasks_with_overlap = sorted(list(set(tasks_with_overlap)))
    with open("task_urls_to_check.txt", "w") as f:
        for task_url in tasks_with_overlap:
            f.write(f"{task_url}\n")

    tasks_with_overlap2 = sorted(list(set(tasks_with_overlap2)))
    with open("task_urls_to_check2.txt", "w") as f:
        for task_url in tasks_with_overlap2:
            f.write(f"{task_url}\n")

    tasks_with_missing_ids = sorted(list(set(tasks_with_missing_ids)))
    with open("task_missing_ids.txt", "w") as f:
        for task_url in tasks_with_missing_ids:
            f.write(f"{task_url}\n")
    
    duplicate_annotation = sorted(list(set(duplicate_annotation)))
    with open("duplicate_annotation.txt", "w") as f:
        for task_url in duplicate_annotation:
            f.write(f"{task_url}\n")

            