import json
from controller import CentralController

c = CentralController()

with open("data/rsvqa_test_sample.json") as f:
    test_data = json.load(f)

correct = 0
total = len(test_data)

for item in test_data:
    image_path = f"data/test_images/{item['img_id']}.tif"
    result, _ = c.route(item["question"], [image_path])
    match = item["answer"].lower() in result.lower()
    if match:
        correct += 1
    else:
        print(f"Q: {item['question']} | Expected: {item['answer']} | Got: {result}")

print(f"\nAccuracy: {correct}/{total} = {correct/total*100:.1f}%")