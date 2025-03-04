# Logcrawler
Scripts for inserting log data into the database. These scripts generally only need to be run once. 

The logcrawler scripts use the [VAAPI pip package](https://pypi.org/project/vaapi/) to communicate with the backend.

You will need these environment variables in order to run the scripts:
```bash
VAT_LOG_ROOT=<"path to folder containing all the log data">
VAT_API_URL=<"http://127.0.0.1:8000/ or https://vat.berlin-united.com/">
VAT_API_TOKEN=<token you can get from the website>
```

## Log folder structure
```
logs/
    2015-07-17_RC15/
    2016-01-16_MM/
    ...
    2018-06-16_RC18/
        comments.txt
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half1/
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half1_to1/
            **[eine Auszeit (TimeOut) ist ein normaler Spielabschnitt, entsprechend enthÃ¤lt er alle Daten wie eine normale Halbzeit]**
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half1_to2/
            **[2. Auszeit]**
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half2/
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
                    **[via Log-Stick gesammelte Daten]**
                    config.zip
                    game.log
                    nao.info
                    patch_labels.json
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
                    half2.LRV
                    half2.MP4
                    half2.url
                        **[enthÃ¤lt einen Link/URL auf ein Video, z.B.: https://www.youtube.com/watch?v=0R39kqXO_KE]**
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half2_penalty/
            **[ElfmeterschieÃŸen (Penalty Shootout) ist ein normaler Spielabschnitt, entsprechend enthÃ¤lt er alle Daten wie eine normale Halbzeit]**


Ein kleiner Kommentar (bestehend aus 1/2 Worten kann durch ein "-" getrennt an das Event, das Spiel oder den Log-Ordner angehÃ¤ngt werden:
logs/
    2018-06-16_RC18-prepare/
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half1-test/
        2018-06-18_15-00-00_Berlin_United_vs_Austin_half2-test/
            game_logs/
                1_91_Nao0379-after-failure
```

The event folder, game folders, log folders, gc_logs folders and the video folder each can have a comments.txt file 


## Access the log folder
If you have a large disk you can download the log folders in the correct structure to your disk and use the logs locally. This is recommended if you want to add a whole event to the database.

TODO: write scripts that downloads all necessary files
Alternatively you can use sshfs. This is much slower then using local files.
TODO add sshfs tutorial here