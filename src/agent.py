import time
try:
    from . import backend
except ImportError:
    import backend
import dotenv
import os
from pathlib import Path
import platformdirs
from jinja2 import Template

print("***** WORKER AGENT STARTER *****")
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
    for key, template_str in config.items():
        template = Template(template_str)
        result = template.render(**map)
            
            # # if the config field is empty, don't append it
            # if key == "status_expiration":
            #     parsed_value = int(parsed_value)
            

        parsed_config[key] = result

        # print(parsed)
    print("===")
    print(parsed_config)  
    print("===")      
    return parsed_config


while True:
    json = hackatime.fetch_hb()
    
    # for _, field in enumerate(json):
    #     key = field
    #     value = json.get(field, "")

    # project = 
    
    
    map = {
        "id": json.get("id", ""),
        "created_at": json.get("created_at", ""),
        "time": json.get("time", ""),
        "category": json.get("category", ""),
        "project": json.get("project", ""),
        "language": json.get("language", ""),
        "editor": json.get("editor", ""),
        "operating_system": json.get("operating_system", ""),
        "machine": json.get("machine", ""),
        "entity": json.get("entity", "")
    }
    
    
    
    print(f'Language: {map["language"]}')
    print("---HT HB---")
    print(json)
    print("---EO HT HB---")
    if "slack" in active_services:
        print(slack.fetch_config())
        config = parse_config(slack.fetch_config(), map)
        print(config)
        
        res = slack.set_profile(config)
        print(res)
    print("---")
    time.sleep(interval)