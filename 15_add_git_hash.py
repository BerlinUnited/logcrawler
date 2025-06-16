"""
add git hash to each log in the database
"""

from vaapi.client import Vaapi
from pathlib import Path
import os

def get_revision_number(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('Revision number:'):
                # Extract the value between quotes
                revision = line.split('"')[1]
                return revision
    return None  # Return None if revision number not found


def main():
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    def sort_key_fn(log):
        return log.id

    logs = client.logs.list()
    for log in sorted(logs, key=sort_key_fn, reverse=True):
        nao_info_file = Path(log_root_path) / Path(log.log_path).parent / "nao.info"
        print(nao_info_file)
        hash = get_revision_number(str(nao_info_file))
        print(hash)
        try:
            client.logs.update(
                id=log.id,
                git_commit=hash
            )
        except Exception as e:
            print("ERROR:", e)
            quit() 


if __name__ == "__main__":
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    main()
