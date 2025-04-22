import log_crawler

# from naoth.log import Parser
import pickle


def get_unparsed_message():
    crawler = log_crawler.LogCrawler(
        "/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/sensor.log"
    )

    all_repr = crawler.get_representation_set()
    print(type(all_repr))
    print(all_repr)
    all_repr.remove("FrameInfo")
    print(all_repr)

    # my_parser = Parser()
    for repr_name in all_repr:
        print(repr_name)
        repr_dict = crawler.get_unparsed_representation_list(repr_name)
        print(repr_dict.keys())

        # print(f"\tparse all {repr_name} messages in python")
        # for data in repr_list:
        #    message = my_parser.parse(repr_name, bytes(data))


def get_parsed_message():
    a = log_crawler.LogCrawler(
        "/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/sensor.log"
    )
    bla = a.get_first_representation2("SensorJointData")
    # bla = a.get_first_representation2("FrameInfo")
    print(f"bla: {bla}")
    print(type(bla))


def main():
    # a = log_crawler.parse_log("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/combined.log")

    # blabla = log_crawler.get_representation("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/sensor.log")
    b = log_crawler.get_representation(
        "/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/combined.log"
    )

    my_message = b[0]
    with open("filename.pickle", "wb") as handle:
        pickle.dump(my_message, handle)


if __name__ == "__main__":
    get_unparsed_message()
