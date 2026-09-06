# code/test_controller.py
from controller import CentralController

c = CentralController()
result, log = c.route(
    "What changed between these images?",
    ["data/demo_images/satellite_1.jpg", "data/demo_images/satellite_2.jpg"]
)
print(result)
print(log)