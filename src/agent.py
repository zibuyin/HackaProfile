import time
try:
    from . import backend
except ImportError:
    import backend
import dotenv
import os
from pathlib import Path
import platformdirs

hackatime = backend.hackatime()
slack = backend.slack()


active_services = ["slack"]
interval = 20
HOME = Path.home()
CONFIG_DIR = Path(platformdirs.user_config_dir("hackaprofile"))
LOG_DIR = Path(platformdirs.user_log_dir("hackaprofile"))


# langauge = ""

pid = os.getpid()
with open(CONFIG_DIR / "agent.pid", "w") as f:
    f.write(str(pid))
    f.close()

def clean_value(value: str) -> str:
    """
    Makes the values clean for slack (Value passed for `name` contained unallowed special characters)
    """
    return value.replace("<", "").replace(">", "")

def parse_config(config: dict, map):
    parsed_config = {}
    for _, field in enumerate(config):
        key = field
        template: str = config[field]
        # Replace {{key}} placeholders directly from the map.
        for map_key, map_value in map.items():
            template = template.replace(map_key, str(map_value))
        try:
            parsed_value = clean_value(template.format_map(map))
            
            # if the config field is empty, don't append it
            if parsed_value != "":
                parsed_config[key] = parsed_value
        except KeyError:
            pass
            
        # print(parsed)
        
    return parsed_config

while True:
    json = hackatime.fetch_hb()
    
    # for _, field in enumerate(json):
    #     key = field
    #     value = json.get(field, "")

    # project = 
    
    
    map = {
        "{{id}}": json.get("id", ""),
        "{{created_at}}": json.get("created_at", ""),
        "{{time}}": json.get("time", ""),
        "{{category}}": json.get("category", ""),
        "{{project}}": json.get("project", ""),
        "{{language}}": json.get("language", ""),
        "{{editor}}": json.get("editor", ""),
        "{{operating_system}}": json.get("operating_system", ""),
        "{{machine}}": json.get("machine", ""),
        "{{entity}}": json.get("entity", "")
    }
    
    
    
    print(f'Language: {map["{{language}}"]}')
    print(json)
    
    if "slack" in active_services:
        print(slack.fetch_config())
        config = parse_config(slack.fetch_config(), map)
        print(config)
        
        res = slack.set_profile(config)
        print(res)
        # for _, field in enumerate(slack_config):
        #     print((field, slack_config[field]))
            
            
        # slack.set_profile(
        #     profile={
        #         "status_text": "test status text",
        #         "status_emoji": ":67:",
        #         "status_expiration": 0
        # })
    print("---")
    time.sleep(interval)
    
    
    
#  