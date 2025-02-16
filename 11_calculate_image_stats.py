from vaapi.client import Vaapi
import requests
import cv2
import os
from tqdm import tqdm
import numpy as np
import argparse
from pathlib import Path
#from PIL import Image 

def is_server_alive(url, timeout=2):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Check for HTTP errors
        print(f"Server {url} is alive.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Server {url} is not reachable: {e}")
        return False


def variance_of_laplacian(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	return cv2.Laplacian(image, cv2.CV_64F).var()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--local", action="store_true", default=False)
    args = parser.parse_args()

    log_root_path = os.environ.get("VAT_LOG_ROOT")
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    
    data = client.logs.list()

    def sort_key_fn(data):
        return data.log_path

    online = is_server_alive("https://logs.berlin-united.com/")

    for data in sorted(data, key=sort_key_fn, reverse=True):
        print("log_path: ", data.id, data.log_path)
        log_id = data.id
        images = client.image.list(log_id=log_id, blurredness_value="None")

        image_data = list()

        for idx, img in enumerate(tqdm(images)):
            if args.local:
                image_path = Path(log_root_path) / img.image_url
                image_cv = cv2.imread(image_path, cv2.IMREAD_COLOR)
            else:
                # try for timeout use the other one if one is not working
                if online:
                    url = "https://logs.berlin-united.com/" + img.image_url
                else:
                    url = "https://logs.naoth.de/" + img.image_url

                response = requests.get(url)
                response.raise_for_status()  # Raise an error for bad status codes

                image = np.asarray(bytearray(response.content), dtype="uint8")
                image_cv = cv2.imdecode(image, cv2.IMREAD_COLOR)

            try:
                gray = cv2.cvtColor(image_cv,cv2.COLOR_BGR2GRAY)
                brightness_value = np.average(gray)
                blurredness_value = variance_of_laplacian(gray)
                height,width,channels = image_cv.shape

                json_obj = {
                     "id": img.id,
                     "blurredness_value":blurredness_value,
                     "brightness_value": brightness_value,
                     "resolution": f"{width}x{height}x{channels}"
                }

                image_data.append(json_obj)

            except Exception as e:
                 print(e)
                 print(f"Image broken at {url} in log: {log_id}")
                 print("This problem can occur if the image extraction for this log was aborted")
                 quit()
            
            if idx % 100 == 0 and idx != 0:
                try:
                    response = client.image.bulk_update(
                        data=image_data
                    )
                    image_data.clear()
                except Exception as e:
                    print(e)
                    print(f"error inputing the data")
                    quit()

        if len(image_data) > 0:
            try:
                response = client.image.bulk_update(
                    data=image_data
                )
            except Exception as e:
                print(e)
                print(f"error inputing the data")
                quit()

