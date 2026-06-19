import time
import backend
hackatime = backend.hackatime()


active_services = ["slack"]
interval = 20

while True:
    json = hackatime.fetch_hb()
    print(json)
    if "slack" in active_services:
        pass
    time.sleep(interval)