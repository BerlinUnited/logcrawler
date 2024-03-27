from minio import Minio
from os import environ

mclient = Minio("minio.berlinunited-cloud.de",
    access_key="naoth",
    secret_key=environ.get("MINIO_PASS"),
)

def remove_all_buckets():
    """
    delete all contents in all buckets and then delete all buckets
    TODO: it should remove all buckets that are referenced in postgres and not delete everything since I need it for other things too
    """
    buckets = mclient.list_buckets()
    for bucket in buckets:
        print(f"deleting bucket {bucket.name}")
        objects_to_delete = mclient.list_objects(bucket.name, recursive=True)
        for obj in objects_to_delete:
            mclient.remove_object(bucket.name, obj.object_name)

        mclient.remove_bucket(bucket.name)


def remove_single_bucket(bucket_name):
    print(f"deleting bucket {bucket_name}")
    objects_to_delete = mclient.list_objects(bucket_name, recursive=True)
    for obj in objects_to_delete:
        mclient.remove_object(bucket_name, obj.object_name)

    mclient.remove_bucket(bucket_name)


def count_images():
    count = 0

    buckets = mclient.list_buckets()
    for bucket in buckets:
        objects = list(mclient.list_objects(bucket.name))
        count += len(objects)

    print(count)


def upload_to_test_buckets():
    mclient.make_bucket("stellatest")
    mclient.fput_object(
            "stellatest",
            "minio_helpers.py",
            "minio_helpers.py",
    )

def delete_bucket_contents(bucket_name):
    objects_to_delete = mclient.list_objects(bucket_name, recursive=True)
    for obj in objects_to_delete:
        print(f"deleting file: {obj.object_name}")
        mclient.remove_object(bucket_name, obj.object_name)
    


if __name__ == "__main__":
    #count_images()
    #upload_to_test_buckets()
    delete_bucket_contents("stellatest")
    remove_single_bucket("stellatest")