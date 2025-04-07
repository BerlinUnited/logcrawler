import log_crawler


def main():
    a = log_crawler.parse_log("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/combined.log")
    b = log_crawler.parse_log("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/sensor.log")
    print()
    print()
    print(a)
    print(type(a))
    print()
    print(b)

if __name__ == "__main__":
    main()