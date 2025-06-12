"""
TODO iterate over all logs and check if the test occurs in logname
"""

from pathlib import Path
import log_crawler
from vaapi.client import Vaapi
import argparse
import os


def main():
    logs = client.logs.list()

    def sort_key_fn(log):
        return log.id

    for log in sorted(logs, key=sort_key_fn):
        print(f"{log.id}: {log.log_path}")
        log_path = log.log_path.lower()
        if "test" in log_path:
            print("\tis part of a testgame")
            client.games.update(
                id=log.game,
                is_testgame=True
            )
        else:
            client.games.update(
                id=log.game,
                is_testgame=False
            )


if __name__ == "__main__":
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    main()