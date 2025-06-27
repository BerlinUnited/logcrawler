# run sudo sshfs naoth@gruenau4.informatik.hu-berlin.de:/vol/repl261-vol4/naoth/logs/ /mnt/repl -o allow_other,ro,uid=33,gid=33,ServerAliveInterval=15,ServerAliveCountMax=3,reconnect

# Set up trap to exit script on Ctrl-C
trap "echo 'Script interrupted by user'; exit 1" SIGINT

file="sensor.log" # **.mp4 combined.log game.log config.zip nao.info
log_root="/mnt/e/logs"

echo "/mnt/repl/2025-03-12-GO25/2025-03-12_21-30-00_BerlinUnited_vs_empty_half1-test"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file  --exclude='*'  /mnt/repl/2025-03-12-GO25/2025-03-12_21-30-00_BerlinUnited_vs_empty_half1-test/ ${log_root}/2025-03-12-GO25/2025-03-12_21-30-00_BerlinUnited_vs_empty_half1-test/

echo "2025-03-12-GO25/2025-03-13_10-10-00_BerlinUnited_vs_Bembelbots_half1"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-13_10-10-00_BerlinUnited_vs_Bembelbots_half1/ ${log_root}/2025-03-12-GO25/2025-03-13_10-10-00_BerlinUnited_vs_Bembelbots_half1/
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-13_10-10-00_BerlinUnited_vs_Bembelbots_half2/ ${log_root}/2025-03-12-GO25/2025-03-13_10-10-00_BerlinUnited_vs_Bembelbots_half2/

echo "2025-03-12-GO25/2025-03-13_17-30-00_BerlinUnited_vs_HTWK_half1"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-13_17-30-00_BerlinUnited_vs_HTWK_half1/ ${log_root}/2025-03-12-GO25/2025-03-13_17-30-00_BerlinUnited_vs_HTWK_half1/
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-13_17-30-00_BerlinUnited_vs_HTWK_half2/ ${log_root}/2025-03-12-GO25/2025-03-13_17-30-00_BerlinUnited_vs_HTWK_half2/

echo "2025-03-14_10-10-00_BerlinUnited_vs_NaoDevils_half1"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-14_10-10-00_BerlinUnited_vs_NaoDevils_half1/ ${log_root}/2025-03-12-GO25/2025-03-14_10-10-00_BerlinUnited_vs_NaoDevils_half1/
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-14_10-10-00_BerlinUnited_vs_NaoDevils_half2/ ${log_root}/2025-03-12-GO25/2025-03-14_10-10-00_BerlinUnited_vs_NaoDevils_half2/

echo "2025-03-14_15-10-00_BerlinUnited_vs_DutchNaoTeam_half1"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-14_15-10-00_BerlinUnited_vs_DutchNaoTeam_half1/ ${log_root}/2025-03-12-GO25/2025-03-14_15-10-00_BerlinUnited_vs_DutchNaoTeam_half1/
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-14_15-10-00_BerlinUnited_vs_DutchNaoTeam_half2/ ${log_root}/2025-03-12-GO25/2025-03-14_15-10-00_BerlinUnited_vs_DutchNaoTeam_half2/

echo "2025-03-12-GO25/2025-03-15_11-40-00_BerlinUnited_vs_BHuman_half1"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-15_11-40-00_BerlinUnited_vs_BHuman_half1/ ${log_root}/2025-03-12-GO25/2025-03-15_11-40-00_BerlinUnited_vs_BHuman_half1/
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-15_11-40-00_BerlinUnited_vs_BHuman_half2/ ${log_root}/2025-03-12-GO25/2025-03-15_11-40-00_BerlinUnited_vs_BHuman_half2/

echo "2025-03-15_15-00-00_BerlinUnited_vs_DutchNaoTeam_half1"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-15_15-00-00_BerlinUnited_vs_DutchNaoTeam_half1/ ${log_root}/2025-03-12-GO25/2025-03-15_15-00-00_BerlinUnited_vs_DutchNaoTeam_half1/
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-15_15-00-00_BerlinUnited_vs_DutchNaoTeam_half2/ ${log_root}/2025-03-12-GO25/2025-03-15_15-00-00_BerlinUnited_vs_DutchNaoTeam_half2/

echo "2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half1"
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half1/ ${log_root}/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half1/
rsync -av --size-only --exclude extracted --include='*/' --progress -h --include=$file --exclude='*' /mnt/repl/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/ ${log_root}/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/