from pathlib import Path
import log_crawler
import os
from vaapi.client import Vaapi
import argparse


def is_done(log_id, status_dict):
    new_dict = status_dict.copy()
    try:
        # we use list here because we only know the log_id here and not the if of the logstatus object
        response = client.log_status.list(log=log_id)
        if len(response) == 0:
            return status_dict
        log_status = response[0]

        invalid_data = False
        for k, v in status_dict.items():
            field_value = getattr(log_status, k)
            # print(k, v, field_value)
            if field_value == None:
                print(f"\tdid not find a value for repr {k}")
            elif field_value > log_status.FrameInfo:
                invalid_data = True
                print(f"\tfound value exceeding number of full frames for repr {k}")
            else:
                new_dict.pop(k)
        # Include FrameInfo when we have representations that exceed the number of FrameInfos
        # Covers the case that the number of FrameInfos was calculated wrongly
        if invalid_data:
            new_dict.update({"FrameInfo": 0})

        return new_dict
    # TODO would be nice to handle the vaapi API error here explicitely
    except Exception as e:
        print("error", e)
        quit()
        return status_dict


def add_gamelog_representations(log, log_path):
    # get list of representations from db
    cognition_repr_names = log.representation_list["cognition_representations"]
    # make a dictionary out of the representation names which can later be used to count
    cognition_status_dict = {item: 0 for item in cognition_repr_names}

    new_cognition_status_dict = is_done(log.id, cognition_status_dict)
    if not args.force and len(new_cognition_status_dict) == 0:
        print("\twe already calculated number of full cognition frames for this log")
    else:
        if args.force:
            new_cognition_status_dict = cognition_status_dict

        # TODO check if new_cognition_status_dict empty
        crawler = log_crawler.LogCrawler(str(log_path))
        new_cognition_status_dict = crawler.get_num_representation()

        print(new_cognition_status_dict)
        try:
            response = client.log_status.update(log=log.id, **new_cognition_status_dict)
        except Exception as e:
            print(f"\terror inputing the data {log_path}")
            print(e)
            quit()


def main():
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    existing_data = client.logs.list()

    def sort_key_fn(dalogta):
        return log.id

    for log in sorted(existing_data, key=sort_key_fn, reverse=True):
        # TODO use combined log if its a file. -> it should always be a file if not experiment
        combined_log_path = Path(log_root_path) / log.combined_log_path

        print(f"{log.id}: {combined_log_path}")
        add_gamelog_representations(log, combined_log_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--force", action="store_true", default=False)
    args = parser.parse_args()

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    main()
