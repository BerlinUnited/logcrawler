# run sudo sshfs naoth@gruenau4.informatik.hu-berlin.de:/vol/repl261-vol4/naoth/logs/ /mnt/repl -o allow_other,ro,uid=33,gid=33,ServerAliveInterval=15,ServerAliveCountMax=3,reconnect

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-15_20-00-00_BerlinUnited_vs_SPQR_half1-test/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-15_20-00-00_BerlinUnited_vs_SPQR_half1-test/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-15_20-00-00_BerlinUnited_vs_SPQR_half2-test/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-15_20-00-00_BerlinUnited_vs_SPQR_half2-test/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-16_20-00-00_BerlinUnited_vs_empty_half1-test/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-16_20-00-00_BerlinUnited_vs_empty_half1-test/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-17_09-00-00_SPQR_vs_BerlinUnited_half1/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-17_09-00-00_SPQR_vs_BerlinUnited_half1/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-17_09-00-00_SPQR_vs_BerlinUnited_half2/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-17_09-00-00_SPQR_vs_BerlinUnited_half2/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-17_16-45-00_BerlinUnited_vs_NaoDevils_half1/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-17_16-45-00_BerlinUnited_vs_NaoDevils_half1/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-17_16-45-00_BerlinUnited_vs_NaoDevils_half2/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-17_16-45-00_BerlinUnited_vs_NaoDevils_half2/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-18_12-30-00_BerlinUnited_vs_Runswift_half1/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-18_12-30-00_BerlinUnited_vs_Runswift_half1/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-18_12-30-00_BerlinUnited_vs_Runswift_half2/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-18_12-30-00_BerlinUnited_vs_Runswift_half2/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-18_12-30-00_BerlinUnited_vs_Runswift_half2-to/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-18_12-30-00_BerlinUnited_vs_Runswift_half2-to/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-18_16-30-00_BerlinUnited_vs_Roboeirean_half1/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-18_16-30-00_BerlinUnited_vs_Roboeirean_half1/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-18_16-30-00_BerlinUnited_vs_Roboeirean_half2/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-18_16-30-00_BerlinUnited_vs_Roboeirean_half2/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-18_16-30-00_BerlinUnited_vs_Roboeirean_half2-to/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-18_16-30-00_BerlinUnited_vs_Roboeirean_half2-to/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-19_09-00-00_BerlinUnited_vs_Nomadz_half1/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-19_09-00-00_BerlinUnited_vs_Nomadz_half1/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-19_09-00-00_BerlinUnited_vs_Nomadz_half1-to/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-19_09-00-00_BerlinUnited_vs_Nomadz_half1-to/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-19_09-00-00_BerlinUnited_vs_Nomadz_half2/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-19_09-00-00_BerlinUnited_vs_Nomadz_half2/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-19_14-30-00_BerlinUnited_vs_BHuman_half1/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-19_14-30-00_BerlinUnited_vs_BHuman_half1/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-19_14-30-00_BerlinUnited_vs_BHuman_half2/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-19_14-30-00_BerlinUnited_vs_BHuman_half2/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-19_22-00-00_BerlinUnited_vs_empty_half1-test/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-19_22-00-00_BerlinUnited_vs_empty_half1-test/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-19_22-00-00_BerlinUnited_vs_empty_half2-test/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-19_22-00-00_BerlinUnited_vs_empty_half2-test/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-20_11-15-00_BerlinUnited_vs_HTWK_Einlauftest/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-20_11-15-00_BerlinUnited_vs_HTWK_Einlauftest/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-20_11-15-00_BerlinUnited_vs_HTWK_half1/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-20_11-15-00_BerlinUnited_vs_HTWK_half1/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-20_11-15-00_BerlinUnited_vs_HTWK_half2/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-20_11-15-00_BerlinUnited_vs_HTWK_half2/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-20_14-15-00_BerlinUnited_vs_Runswift_half1/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-20_14-15-00_BerlinUnited_vs_Runswift_half1/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-20_14-15-00_BerlinUnited_vs_Runswift_half2/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-20_14-15-00_BerlinUnited_vs_Runswift_half2/game_logs/

rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-21_12-00-00_BerlinUnited_vs_NaoDevils_half1-test/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-21_12-00-00_BerlinUnited_vs_NaoDevils_half1-test/game_logs/
rsync -avv --include='*/' --progress -h --include='combined.log' --exclude='*' /mnt/repl/2024-07-15_RC24/2024-07-21_12-00-00_BerlinUnited_vs_NaoDevils_half2-test/game_logs/ /mnt/d/logs/2024-07-15_RC24/2024-07-21_12-00-00_BerlinUnited_vs_NaoDevils_half2-test/game_logs/









