try:
    from . import hackatimeOA
    from . import slackOA
except ImportError:
    import hackatimeOA
    import slackOA
import keyring
import requests
import dotenv
from pathlib import Path


service_name = "HackaProfile"
HOME = Path.home()
CONFIG_DIR_PATH = HOME / ".config" / "hackaprofile" / "config"

# config = dotenv.dotenv_values("../config/.conf")


class hackatime():
    def __init__(self) -> None:
        self.hb_url = "https://hackatime.hackclub.com/api/v1/authenticated/heartbeats/latest"
        self.username = "hackatime_token"
        self.config_path = CONFIG_DIR_PATH / "hackatime.hackaprofile.conf"
        # self.client_id = self.load_config()["client_id"]
    # Authorize hackatime
    def authorize(self) -> tuple:
        token = hackatimeOA.authenticate()
        # If token is given:
        if type(token) == str and token:
            self.store_token(token)
            return (True, token)
        else:
            return (False, token)
    
    def revoke(self):
        url = "https://hackatime.hackclub.com/oauth/revoke"
        print(self.fetch_config()["client_id"])
        headers = {
        "Authorization": f"Bearer {self.get_token()}"
        }
        data = {
            "token": self.get_token(),
            "client_id": self.fetch_config()["client_id"],
        }
        
        # dataJson = json.dumps(data)
        # print(dataJson)
        return requests.post(url=url, data=data).json()

    def get_token(self) -> str:
        token = keyring.get_password(service_name, self.username)
        if type(token) != str:
            token = ""
        return token
    
    def store_token(self, token: str) -> None:
        keyring.set_password(service_name, self.username, token)
    
    def fetch_hb(self):
        url = self.hb_url
        headers = {
            "Authorization": f"Bearer {self.get_token()}"
        }
        try:
            res = requests.get(url=url, headers=headers)
            json = res.json()
        except:
            json = {"ok": False}
        return json
    
    def fetch_config(self) -> dict:
        return dotenv.dotenv_values(self.config_path)
    
    def status(self):
        json = self.fetch_hb()
        # print(json)
        
        # Hackatime does not return ok if its ok. Weird...
        ok = json.get("ok", True)
        if ok == False:
            error = json.get("error", "")
        else:
            error = ""
        return {"ok": ok, "error": error}
    def load_config(self) -> dict:
        return dotenv.dotenv_values(self.config_path)


class slack():
    def __init__(self) -> None:
        self.base_url = "https://slack.com/api"
        self.username = "slack_token"
        self.config_path = CONFIG_DIR_PATH / "slack.hackaprofile.conf"
        # self.client_id = self.load_config()["client_id"]
    # Authorize hackatime
    def authorize(self) -> tuple:
        token = slackOA.authenticate()
        # If token is given:
        if type(token) == str and token:
            self.store_token(token)
            return (True, token)
        else:
            return (False, token)
            
    def get_token(self) -> str:
        token = keyring.get_password(service_name, self.username)
        if type(token) != str:
            token = ""
        return token
    
    def store_token(self, token: str) -> None:
        keyring.set_password(service_name, self.username, token)
        
    def set_profile(self, profile: dict) -> dict:
        url = f"{self.base_url}/users.profile.set"
        headers = {
        "Authorization": f"Bearer {self.get_token()}"
        }
        data = {
            "profile": profile
        }
        
        # dataJson = json.dumps(data)
        # print(dataJson)
        return requests.post(url=url, headers=headers, json=data).json()

    def get_profile(self):
        url = f"{self.base_url}/users.profile.get"
        headers = {
        "Authorization": f"Bearer {self.get_token()}"
        }
        
        # dataJson = json.dumps(data)
        # print(dataJson)
        return requests.get(url=url, headers=headers).json()
    
    # Get the field id <-> label pairs
    def get_team_profile(self):
        url = f"{self.base_url}/team.profile.get"
        headers = {
        "Authorization": f"Bearer {self.get_token()}"
        }
        
        # dataJson = json.dumps(data)
        # print(dataJson)
        return requests.get(url=url, headers=headers).json()
    
    def fetch_config(self) -> dict:
        return dotenv.dotenv_values(self.config_path)
    
    def status(self):
        pass
        # json = self.fetch_hb()
        # # print(json)
        
        # # Hackatime does not return ok if its ok. Weird...
        # ok = json.get("ok", True)
        # if ok == False:
        #     error = json.get("error", "")
        # else:
        #     error = ""
        # return {"ok": ok, "error": error}
        
        
    def load_config(self) -> dict:
        return dotenv.dotenv_values(self.config_path)

platfroms = {
    "slack": slack,
}