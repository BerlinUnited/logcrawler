# Logcrawler
Scripts for inserting log data into the database. These scripts generally only need to be run once per game folder.

The logcrawler scripts use the [VAAPI pip package](https://pypi.org/project/vaapi/) to communicate with the [database backend](https://github.com/BerlinUnited/Visual-Analytics) and the [Naoth pip package](https://pypi.org/project/naoth/) to parse the logs. The logcrawler expects the folder structure that is described below and will only work correctly if the data is in this structure. We developed a couple of standalone scripts in the standalone folder.

## Log folder structure
```
logs/
    ...
    2024-07-15_RC24/
        comments.txt
        ...
        2024-07-18_16-30-00_BerlinUnited_vs_Roboeirean_half1
        2024-07-18_16-30-00_BerlinUnited_vs_Roboeirean_half2
        2024-07-18_16-30-00_BerlinUnited_vs_Roboeirean_half2-to
            **a timeOut (to) is a normal part of the game therefor we treat it as if it would be an additional half**
            **the folder with the -to suffix contains data from when the game was resumed after timeout was called**
            **if a second timeout is called in a game we would use the suffix -to2**
    2025-03-12-GO25/
        comments.txt
        2025-03-12_21-30-00_BerlinUnited_vs_empty_half1-test/
            **the -test suffix indicates a testgame that we recorded similar to a realy game, we are not logging experiment logs but game.logs**
        2025-03-13_17-30-00_BerlinUnited_vs_HTWK_half1/
        2025-03-13_17-30-00_BerlinUnited_vs_HTWK_half2/
            comments.txt
            extracted/
                1_91_Nao0379/
                2_97_Nao0075/
                3_94_Nao0338/
                4_96_Nao0377/
                5_95_Nao0225/
                    **[generierte Daten]**
                    log.json
                gc.json
                videos.json
            game_logs/
                1_91_Nao0379/
                2_97_Nao0075/
                3_94_Nao0338/
                4_96_Nao0377/
                5_95_Nao0225/
                    **[data recorded by the robot and collected via USB-Stick]**
                    config.zip
                    game.log
                    nao.info
                    comments.txt
                    ...
            gc_logs/
                    teamcomm_2018-06-18_15-16-19-611_UT Austin Villa_Berlin United_2ndHalf_initial.log
                    teamcomm_2018-06-18_15-21-23-346_UT Austin Villa_Berlin United_2ndHalf.log
                    teamcomm_2018-06-18_15-21-23-346_UT Austin Villa_Berlin United_2ndHalf.log.gtc.json
                    teamcomm_2018-06-18_15-32-25-912_UT Austin Villa_Berlin United_2ndHalf_finished.log
                    comments.txt
            videos/
                    comments.txt
                    half2.mp4
                    half2.url
                        **[enthält einen Link/URL auf ein Video, z.B.: https://www.youtube.com/watch?v=0R39kqXO_KE]**
        videos/
            **Contains videos of other games**
            2025-03-16_xx-xx-00_B-Human_vs_Hulks_half1_Field-A_GoPro.mp4
            2025-03-16_xx-xx-00_B-Human_vs_Hulks_half1_Field-A_PiCam.mp4
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half2_penalty/
            **[Elfmeterschießen (Penalty Shootout) ist ein normaler Spielabschnitt, entsprechend enthÃ¤lt er alle Daten wie eine normale Halbzeit]**
            **TODO each penalty shoot is its own half - how is this communicated by the gamecontroller and how can we name the videos and folders for this**
            ** there are some instances of penalty shootout in go25 **
            ** TODO how to handle penalty shootout vs sudden death shootout?**

**TODO: the comments file is better place for this maybe? - think of scenarios that happen where we need this also take into account what is easiest to parse**
Ein kleiner Kommentar (bestehend aus 1/2 Worten kann durch ein "-" getrennt an das Event, das Spiel oder den Log-Ordner angehÃ¤ngt werden:
logs/
    2018-06-16_RC18-prepare/
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half1-test/
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half2-test/
            game_logs/
                1_91_Nao0379-after-failure
```

The event folder, game folders, log folders, gc_logs folders and the video folder each can have a comments.txt file 

## Development
You will need these environment variables in order to run the scripts:
```bash
VAT_LOG_ROOT=<"path to folder containing all the log data">
VAT_API_URL=<"http://127.0.0.1:8000/ or https://vat.berlin-united.com/">
VAT_API_TOKEN=<you need to ask the maintainer for a token>
```

For development we recommend using an .envrc file which enables you to quickly change those values.

### Access the log folder
If you have a large disk you can download the log folders in the correct structure to your disk and use the logs locally. This is recommended if you want to add a whole event to the database.

TODO: write scripts that downloads all necessary files
Alternatively you can use sshfs. This is much slower then using local files.
TODO add sshfs tutorial here


### The C part
The extract_images.py script needs to verify how many images are in the extracted folder. ls is really slow if you have a couple thousand files in one folder. We wrote our own fast_ls program that is much faster. The difference is most noteable if you access the log folder over network.

You can build the fast_ls binary with
```bash
gcc scripts/fast_ls.c -o fast_ls
```

### Build Rust Part
Install rust: https://doc.rust-lang.org/stable/book/ch01-01-installation.html

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt

maturin develop
python tests/rusty.py
```

You need to change the path to the logfile in the python script

TODO: explain the protos folder

### Ruff

