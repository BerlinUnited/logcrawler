from dataclasses import dataclass
from label_studio_sdk import Client
from patch_exporter.helper import BoundingBox, Point2D

LABEL_STUDIO_URL = "https://ls.berlin-united.com/"
API_KEY = "6cb437fb6daf7deb1694670a6f00120112535687"

@dataclass
class Annotation:
    id_: str
    label: str
    bbox: BoundingBox

@dataclass
class Overlap:
    a1: Annotation
    a2: Annotation


def get_annotations_from_task(task: dict):
    annotations = task["annotations"]

    annotation_objs = []

    for annotation in annotations:
        for result in annotation["result"]:
            if result["type"] != "rectanglelabels":
                continue

            id_ = result["id"]
            label = result["value"]["rectanglelabels"][0]
            bbox = bbox_from_result(result)

            annotation_obj = Annotation(id_, label, bbox) 
            annotation_objs.append(annotation_obj)

    return annotation_objs

def bbox_from_result(result: dict):
    x = result["value"]["x"]
    y = result["value"]["y"]
    width = result["value"]["width"]
    height = result["value"]["height"]
    return BoundingBox(Point2D(x, y), Point2D(x + width, y + height))

def get_overlapping_boxes(annotations: list[Annotation]):
    overlapping_boxes = []

    for i, a1 in enumerate(annotations):
        for j, a2 in enumerate(annotations):
            if i == j:
                continue

            if a1.bbox.intersection(a2.bbox) is not None:
                overlap = Overlap(a1, a2)
                overlapping_boxes.append(overlap)

    return overlapping_boxes

def get_all_labeled_tasks(ls: Client):
    print("Fetching all projects...")
    projects = ls.get_projects()

    print(f"Fetching all labeled tasks from {len(projects)} projects...")
    labeled_tasks = [task for project in projects for task in project.get_labeled_tasks()]
    return labeled_tasks

def get_project_url_from_task(task: dict):
    project_id = task["project"]
    task_id = task["id"]
    return f"{LABEL_STUDIO_URL}/projects/{project_id}/data?task={task_id}"

if __name__ == "__main__":
    ls = Client(url=LABEL_STUDIO_URL, api_key=API_KEY)
    ls.check_connection()

    labled_tasks = get_all_labeled_tasks(ls)
    tasks_with_overlap = []

    for task in labled_tasks:
        print(f"Checking task {task['id']}...")
        try:
            annotations = get_annotations_from_task(task)
            overlapping_boxes = get_overlapping_boxes(annotations) 

            # we are only interested in overlapping boxes with different labels
            # e.g. ball and nao, or penalty_mark and ball
            for overlap in overlapping_boxes:
                if overlap.a1.label != overlap.a2.label:
                    task_url = get_project_url_from_task(task)
                    tasks_with_overlap.append(task_url)
        except Exception as e:
            print(f"Error while checking task {task['id']}: {e}")
    
    tasks_with_overlap = sorted(list(set(tasks_with_overlap)))
    with open("task_urls_to_check.txt", "w") as f:
        for task_url in tasks_with_overlap:
            f.write(f"{task_url}\n")