from pathlib import Path
import os
import log_crawler
from vaapi.client import Vaapi
import argparse


def is_done_motion(log_id, status_dict):
    new_dict = status_dict.copy()
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log=log_id)
        if len(response) == 0:
            return status_dict
        log_status = response[0]

        for k, v in status_dict.items():
            if k == "FrameInfo":
                field_value = getattr(log_status, "num_motion_frames")
            else:
                field_value = getattr(log_status, k)

            if field_value is None:
                print(f"\tdid not find a value for repr {k}")
            else:
                new_dict.pop(k)
        return new_dict
    # TODO would be nice to handle the vaapi API error here explicitely
    except Exception as e:
        print("error", e)
        quit()
        return status_dict


def add_sensorlog_representations(log, sensor_log_path):
    # get list of representations from db
    motion_repr_names = log.representation_list["motion_representations"]
    # make a dictionary out of the representation names which can later be used to count
    motion_status_dict = {item: 0 for item in motion_repr_names}

    new_motion_status_dict = is_done_motion(log.id, motion_status_dict)
    if not args.force and len(new_motion_status_dict) == 0:
        print("\twe already calculated number of full sensor frames for this log")
    else:
        if args.force:
            new_motion_status_dict = motion_status_dict

        crawler = log_crawler.LogCrawler(str(sensor_log_path))
        new_motion_status_dict = crawler.get_num_representation()

        try:
            if "FrameInfo" in new_motion_status_dict:
                new_motion_status_dict["num_motion_frames"] = (
                    new_motion_status_dict.pop("FrameInfo")
                )

            print(new_motion_status_dict)
            _ = client.log_status.update(log=log.id, **new_motion_status_dict)
        except Exception as e:
            print(f"\terror inputing the data {sensor_log_path}")
            print(e)
            quit()


def main(args):
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    existing_data = client.logs.list()

    def sort_key_fn(log):
        return log.id

    for log in sorted(existing_data, key=sort_key_fn, reverse=args.reverse):
        sensor_log_path = Path(log_root_path) / log.sensor_log_path

        print(f"{log.id}: {sensor_log_path}")
        add_sensorlog_representations(log, sensor_log_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true", default=False)
    parser.add_argument("-r", "--reverse", action="store_true", default=False)
    args = parser.parse_args()

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    main(args)
