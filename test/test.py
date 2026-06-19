import requests
import time
import keyring
import slackOA
import hackatimeOA
import json

slackBaseUrl = "https://slack.com/api"
hackatimeHBUrl = "https://hackatime.hackclub.com/api/v1/authenticated/heartbeats/latest"

def init():
    slackToken = slackOA.authenticate()
    hackatimeToken = hackatimeOA.authenticate()

    if type(slackToken) != str:
        print(slackToken)
        slackToken = ""

    if type(hackatimeToken) != str:
        print(hackatimeToken)
        hackatimeToken = ""
        
    keyring.set_password("SlackPFP", "slackToken", slackToken)
    keyring.set_password("SlackPFP", "hackatimeToken", hackatimeToken)


# If is first time running
# if not keyring.get_password("SlackPFP", "hackatimeToken"):
# init()

slackToken = keyring.get_password("SlackPFP", "slackToken")
hackatimeToken = keyring.get_password("SlackPFP", "hackatimeToken")

# Helper func
def slack(endpoint):
    return f"{slackBaseUrl}/{endpoint}"

def changeSlackPFP(path):
    print("changing pfp")
    with open(path, "rb") as f:
        files = {
            "image": f
        }
        headers = {
            "Authorization": f"Bearer {slackToken}"

        }
        res = requests.post(url=slack("users.setPhoto"), headers=headers, files=files)
        print(res.json())

def updateSlackStatus(text: str, emoji: str, exp: int):
    url = slack("users.profile.set")
    headers = {
        "Authorization": f"Bearer {slackToken}"
    }
    data = {
        "profile": {
            "status_text": text,
            "status_emoji": emoji,
            "status_expiration": exp
        }
    }
    
    # dataJson = json.dumps(data)
    # print(dataJson)
    return requests.post(url=url, headers=headers, json=data).json()

def fetchHeartbeat():
    url = hackatimeHBUrl
    headers = {
        "Authorization": f"Bearer {hackatimeToken}"
    }
    res = requests.get(url=url, headers=headers)
    return res.json()

# print(fetchHeartbeat())

while True:
    hb = fetchHeartbeat()
    print(hb)
    language = hb["language"]
    category = hb["category"]

    print(language)
    # if category == "coding" and language:
    if not language:
        emoji = ""
        text = ""
    else:
        emoji = f":{language.lower()}:"
        text = f"Typing in {language}..."
    print(updateSlackStatus(text, emoji , 0))
    time.sleep(20)
