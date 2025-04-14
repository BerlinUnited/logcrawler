import log_crawler
import time
start = time.time()
a = log_crawler.LogCrawler("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/combined.log")
end = time.time()
print(end - start)
print()
b = a.get_representation_set()
#print(b)
print(a.get_num_representation())
start = time.time()
blub = a.get_representation()
end = time.time()
print(end - start)
#print(a.log_path)

#a = log_crawler.get_representation("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/combined.log")