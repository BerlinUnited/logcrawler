def input_other_video_data(log_root_path, client):
    events = client.events.list()
    for event in events:
        ev = Path(log_root_path) / event.event_folder
        all_games = [f for f in ev.iterdir() if f.is_dir()]
        for game in sorted(all_games):
            logging.debug(f"parsing folder {game}")
            if str(game.name).lower() != "videos":
                continue
            
            # TODO handle videos from other teams here