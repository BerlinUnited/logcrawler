import log_crawler
from naoth.log import Parser
from PIL import Image as PIL_Image
import numpy as np
import io
import pickle

def get_representation_message():
    a = log_crawler.LogCrawler("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/sensor.log")
    bla = a.get_first_representation("SensorJointData")
    my_parser = Parser()
    message = my_parser.parse("SensorJointData", bytes(bla[0]))
    #print(bla)
    print()
    # print parsed message from rust
    print(message)
    print()

    bla = a.get_first_representation2("SensorJointData")
    print(f"bla: {bla}")
    print(type(bla))

def main():
    #a = log_crawler.parse_log("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/combined.log")
    
    
    #blabla = log_crawler.get_representation("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/sensor.log")
    b = log_crawler.get_representation("/mnt/d/logs/2025-03-12-GO25/2025-03-15_17-15-00_BerlinUnited_vs_Hulks_half2/game_logs/7_33_Nao0022_250315-1822/combined.log")
    
    my_message = b[0]
    with open('filename.pickle', 'wb') as handle:
        pickle.dump(my_message, handle)
    
    

if __name__ == "__main__":
    get_representation_message()