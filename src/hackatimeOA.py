from flask import Flask, request
import requests
import secrets
import hashlib
import base64
import webbrowser
from werkzeug.serving import make_server
import threading
import time
import logging
import dotenv
from pathlib import Path
import platformdirs
from rich import print as rprint

log = logging.getLogger('werkzeug')

log.setLevel(logging.ERROR)

stateRNG = secrets.token_urlsafe(32)
baseUrl = "https://hackatime.hackclub.com/oauth/authorize"
exchangeBaseUrl = "https://hackatime.hackclub.com/oauth/token"
redirection_uri = "http://localhost:32767/auth/hackatime/callback"
headless = False

headless_redirection_uri = "https://authforward.nathanyin.workers.dev"


# headless_redirection_uri = "http://localhost:5500"


CONFIG_DIR = Path(platformdirs.user_config_dir("hackaprofile"))
LOG_DIR = Path(platformdirs.user_log_dir("hackaprofile"))

# print(client_id)
token = ""
code_verifier = ""
client_id = ""
headless_global = False
token_event = threading.Event()
# Redirect to the auth page
def redirection(state):
    # print("debug")
    global code_verifier, client_id
    
    # Just an unique id, not secret lol
    client_id = dotenv.dotenv_values(CONFIG_DIR / "hackatime.hackaprofile.conf")["client_id"]


    code_verifier = secrets.token_urlsafe(664)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip('=')
    args = {
        "client_id": client_id,
        "redirect_uri": redirection_uri,
        "response_type": "code",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    url = requests.Request("GET", baseUrl, params=args).prepare().url
    if url is None:
        raise RuntimeError("Failed to construct authorization URL")
    
    if not headless_global:
        webbrowser.open(url)
    else:
        rprint("Please open this URL in your browser:\n")
        print(url)
        print("\n")
    if headless_global:
        headlessCallback()


# Exchange API key
def exchange(code: str):
    global token_event
    url = exchangeBaseUrl
    data = {
        "client_id": client_id,
        "code": code,
        "redirect_uri": redirection_uri,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
        
    }
    res = requests.post(url=url, data=data)
    json = res.json()
    token_event.set()
    if not json.get("error"):
        token = json.get("access_token")
        # print(token)
        return token
    else:
        return {"error": json.get("error")}
# Handle callback
app = Flask(__name__)

@app.route("/auth/hackatime/callback")
def hackatimeCallback():
    global token
    code = request.args.get("code")
    error = request.args.get("error")
    state2 = request.args.get("state")
    # print(code)
    
    if not error and code and state2 == stateRNG:
        token = exchange(code)
        # print(token)
        return "<p>Authorization completed, you can close this tab now.</p>"
    else:
        return "<p>You have denied authorization, or an error has occured.</p><p>If you did not deny authorization, please close this tab and submit a issue on Github</p>"

def headlessCallback() -> None:
    global token
    token = exchange(input("Please input the code that appeared on the screen: ")
)

def authenticate(headless: bool):
    global redirection_uri, headless_global
    headless_global = headless
    # Overwrite the uri with headless uri if configured as so
    if headless:
        redirection_uri = headless_redirection_uri  
        
    redirection(stateRNG)
    
    server = make_server("127.0.0.1", 32767, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    
    token_event.wait(timeout=120)
        
    
    server.shutdown()
    thread.join()
    return token



# Debug
if __name__ == "__main__":
    authenticate(headless=False)