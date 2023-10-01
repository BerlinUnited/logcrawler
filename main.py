"""
"""
import pathlib
import time

# folder path
dir_path = '/mnt/repl/'
# construct path object
d = pathlib.Path(dir_path)

while True:
    # iterate directory
    for entry in d.iterdir():
        # check if it a file
        print(entry)

    time.sleep(5)