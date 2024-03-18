from minio import Minio
mclient = Minio("minio.berlinunited-cloud.de",
    access_key="naoth",
    secret_key="HAkPYLnAvydQA",
)

def remove_all_buckets():
    """
    delete all contents in all buckets and then delete all buckets
    """
    buckets = mclient.list_buckets()
    for bucket in buckets:
        print(f"deleting bucket {bucket.name}")
        objects_to_delete = mclient.list_objects(bucket.name, recursive=True)
        for obj in objects_to_delete:
            mclient.remove_object(bucket.name, obj.object_name)

        mclient.remove_bucket(bucket.name)


def count_images():
    count = 0

    buckets = mclient.list_buckets()
    for bucket in buckets:
        objects = list(mclient.list_objects(bucket.name))
        count += len(objects)

    print(count)

if __name__ == "__main__":
    #count_images()
    remove_all_buckets()