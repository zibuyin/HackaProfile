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

log = logging.getLogger('werkzeug')

log.setLevel(logging.ERROR)

stateRNG = secrets.token_urlsafe(32)
baseUrl = "https://hackatime.hackclub.com/oauth/authorize"
exchangeBaseUrl = "https://hackatime.hackclub.com/oauth/token"
redirection_uri = "http://localhost:32767/auth/hackatime/callback"


# print(client_id)
token = ""
code_verifier = ""
client_id = ""

token_event = threading.Event()
# Redirect to the auth page
def redirection(state):
    # print("debug")
    global code_verifier, client_id
    
    # Just an unique id, not secret lol
    client_id = dotenv.dotenv_values("../config/hackatime.hackaprofile.conf")["client_id"]


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
        "state": state,
    }
    url = f"{baseUrl}/?client_id={args['client_id']}&redirect_uri={args["redirect_uri"]}&response_type=code&state={args["state"]}&code_challenge={args["code_challenge"]}&code_challenge_method={args["code_challenge_method"]}&state={args["state"]}"
    
    webbrowser.open(url)


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
    

def authenticate():
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
    authenticate()