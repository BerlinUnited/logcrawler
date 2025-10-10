import os
import Vaapi
from pathlib import Path
import logging
if __name__ == "__main__":
    log_root_path = os.environ.get("VAT_LOG_ROOT")

    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    #todo wait until VAT add_team_view branch is ready
    events = client.events.list()
    for event in events:
        ev = Path(log_root_path) / event.event_folder
        all_games = [f for f in ev.iterdir() if f.is_dir()]
        for game in sorted(all_games):
            try:
                game_parsed = str(game.name).split("_")
                timestamp = game_parsed[0] + "_" + game_parsed[1]
                team1 = game_parsed[2]
                team2 = game_parsed[4]
                halftime = game_parsed[5]
            except Exception as e:
                logging.error(f'{e} when parsing {game.name} folder')
            
    
    