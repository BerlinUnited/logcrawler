from minio import Minio
mclient = Minio("minio.berlinunited-cloud.de",
    access_key="naoth",
    secret_key="HAkPYLnAvydQA",
)

def remove_all_buckets():
    # TODO not sure if this works or if I need to delete the objects in it before
    buckets = mclient.list_buckets()
    for bucket in buckets:
        mclient.remove_bucket(bucket.name)


def count_images():
    count = 0

    buckets = mclient.list_buckets()
    for bucket in buckets:
        objects = list(mclient.list_objects(bucket.name))
        count += len(objects)

    print(count)

count_images()