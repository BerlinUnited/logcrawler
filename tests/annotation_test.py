from vaapi.client import Vaapi
import os
import uuid
"""
{
    "x": ( cx - ( width / 2 ) ) / 640,
    "y": ( cy - ( height / 2 ) ) / 480,
    "id":uuid.uuid4().hex[:9].upper(),
    "label":class_mapping[int(class_id)],
    "width": width / 640,
    "height": height / 480
}
"""
def create_annotation():
    my_json1 = {
        "x": 100,
        "y": 100,
        "id":uuid.uuid4().hex[:9].upper(),
        "width": 300,
        "height": 200
    }
    my_json2 = {
        "x": 400,
        "y": 400,
        "id":uuid.uuid4().hex[:9].upper(),
        "width": 50,
        "height": 50
    }

    #response = client.annotations.create(
    #    image_id=7667304,
    #    type="bbox",
    #    class_name="ball",
    #    data=my_json1,
    #)
    response = client.annotations.create(
        image_id=7667304,
        type="bbox",
        class_name="ball",
        data=my_json2,
    )
    print(response)


if __name__ == "__main__":
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )

    a = client.annotations.list(image=7667304)
    print(a)