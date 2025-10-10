from vaapi.client import Vaapi
from utils import check_env_vars
from ingester import input_events
from ingester import input_games
from utils import check_folder_exists
import logging
import os

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    check_env_vars()
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    if not check_folder_exists(log_root_path):
        logging.getLogger().error(f"Log Path at {log_root_path} is not accessible")

    # TODO catch errors here
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    input_events(log_root_path, client)
    input_games(log_root_path, client)
