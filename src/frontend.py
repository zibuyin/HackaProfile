import time
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console, Group
from rich.text import Text
from rich.pretty import Pretty, pprint
from rich.prompt import Confirm
from rich.table import Table
from rich import box
from rich.live import Live
from rich.highlighter import Highlighter
# from rich.terminal_theme import MONOKAI

import typer
from typing import Annotated

try:
    from . import backend
except ImportError:
    import backend

import questionary

import os
import shutil
from pathlib import Path
import dotenv
import pyperclip

import subprocess as sp

import sys
import psutil
import signal
console = Console()

app = typer.Typer(no_args_is_help=True)
hackatime = backend.hackatime()
slack = backend.slack()
HOME = Path.home()
CONFIG_DIR_PATH = HOME / ".config" / "hackaprofile" / "config"

@app.callback()
def callback():
    """
    Useful tool to automatically update online profiles based on Hackatime status
    """
    
# Auto completion
def complete_platform(incomplete: str) -> list:
    valid_names = ["HackaTime", "Slack"]
    completion = []
    for name in valid_names:
        if name.startswith(incomplete):
            completion.append(name)
    return completion

@app.command()
def status():
    """
    View the status of HackaProfile
    """
    parsed_hackatime_status = {}
    parsed_slack_status = {}
    
    with console.status("Fetching status...", spinner="dots"):
        hackatime_status: dict = hackatime.fetch_hb()
        
        temp = slack.get_profile()
        # rprint(temp)
        try:
            slack_status: dict = temp["profile"]
        except KeyError:
            # If there is an error
            slack_status: dict = temp
        # rprint(slack_status)
        
    if hackatime_status.get("ok", True) == False:
        parsed_hackatime_status["Authorization"] = "❌ Unauthorized"
    else:
        parsed_hackatime_status["Authorization"] = "[bold green]✓[/bold green] Authorized"
        parsed_hackatime_status["Current Language"] = hackatime_status.get("language", "Unknown")
        parsed_hackatime_status["Current Project"] = hackatime_status.get("project", "Unknown")
        
    # print(slack_status)
    if slack_status.get("ok") == False:
        parsed_slack_status["Authorization"] = f"❌ {slack_status.get("error", "Unknown error")}"
    else:
        parsed_slack_status["Authorization"] = "[bold green]✓[/bold green] Authorized"
        parsed_slack_status["Display Name"] = slack_status.get("display_name", "Unknown")
        parsed_slack_status["Status Text"] = slack_status.get("status_text", "Unknown")
        parsed_slack_status["Status Emoji"] = slack_status.get("status_emoji", "Unknown")
        
    
    hackatime_table = Table("Field", "Value", title="Hackatime", box=box.ROUNDED, expand=True)
    slack_table = Table("Field", "Value", title="Slack", box=box.ROUNDED, expand=True)
    
    for _, field in enumerate(parsed_hackatime_status):
        key = field
        value = parsed_hackatime_status[field]
        hackatime_table.add_row(key, value)
        
    for _, field in enumerate(parsed_slack_status):
        key = field
        value = parsed_slack_status[field]
        slack_table.add_row(key, value)
    
    grid = Table.grid(expand=True, padding=10)
    grid.add_column()
    grid.add_column(justify="right")
    grid.add_row(hackatime_table, slack_table)
    rprint(
        "",
        grid
    )
    

# [bold green]✓[/bold green]
def authorizeHA():
    ok, hatoken = hackatime.authorize()
    # If token is given:
    if ok:
        rprint("[bold green]✓[/bold green] Hackatime authorized!")
        return hatoken
    else:
        rprint(f"[bold red]err: {str(hatoken)}")
        hatoken = authorizeHA()
        
    return hatoken

@app.command()
def setup(force: Annotated[bool, typer.Option("--force")] = False):
    """
    Guided setup of HackaProfile
    """
    console.clear()
    # console.rule("HackaProfile")
    rprint(Panel(Text("Welcome to HackaProfile\nyou will be guided on an easy setup of the tool!", justify="center")))
    console.rule()
    # rprint(force)
    
    # Copy config files
    try:
        # Allow overwrite if set to force
        shutil.copytree(Path(__file__).resolve().parent.parent / "configTemplate", CONFIG_DIR_PATH, dirs_exist_ok=force)
        rprint("[bold green]✓[/bold green] Config file setup done!")
    except FileExistsError:
        rprint("[bold green]✓[/bold green] Config file already exists!")
    except Exception as e:
        rprint(f"❌ Failed to setup config files: {e}")
        
        
    
    # If no token stored
    if force or not hackatime.status()["ok"]:
        # hackatimeConfirm = Confirm.ask("[bold cyan]Do you want to authorize Hackatime (This will redirect you to OAuth page)", default=True)
        hackatimeConfirm  = questionary.confirm("Do you want to authorize Hackatime (This will redirect you to OAuth page)").ask()
        if hackatimeConfirm:
            with console.status("Authorizing Hackatime", spinner="dots"):
                ok, hackatime_token = hackatime.authorize()
                
            if ok:
                rprint("[bold green]✓[/bold green] Hackatime authorized!")
                
            else :
                rprint(f"[bold red]err: {str(hackatime_token)}")    
        else:
            rprint("[bold red]err: HackaProfile could not function without Hackatime.")
            typer.Abort()
    # If already stored
    else:
        rprint("[bold green]✓[/bold green] Hackatime already authorized!\n")
        
    platforms = questionary.checkbox(
        message="Please choose the platforms you want to link to",
        choices=[
            "Slack",
            "Github"
        ]
    ).ask()
    
    # Authorize the platforms
    
    for platform in platforms:
        # print("test")
        cls = backend.platfroms.get(platform.lower())
        if cls:
            instance = cls()
            with console.status(f"Authorizing {platform}", spinner="dots"):
                ok, platform_token = instance.authorize()
            if ok:
                rprint(f"[bold green]✓[/bold green] {platform} authorized!")
                
            else:
                rprint(f"[bold red]err: {str(platform_token)}")
            
        else:
            rprint("[bold red]err: Platform unsupported")
        
        
    rprint("[bold green]✓[/bold green] Setup complete!\n\n1.Run [bold green]hackaprofile config \\[platform name][/bold green] to configure\n2.Run [bold green]hackaprofile start[/bold green] to start updating your profile automatically!")
        
class placeholderHighlighter(Highlighter):
    def highlight(self, text) -> None:
        text.highlight_regex(r"\{\{.*?\}\}", "bold yellow")
        
@app.command()
def config(platform: Annotated[str, typer.Argument]):
    table = Table(
        "Field",
        "Value",
        title="Preview Slack",
        box=box.ROUNDED,
        expand=True,
    )
    
    hlt = placeholderHighlighter()
    slack_config_keys = list(slack.load_config().keys())
    slack_config_values = list(slack.load_config().values())
    
    for i in range(len(slack_config_keys)):
        field = slack_config_keys[i]
        value = slack_config_values[i]
        if not value:
            value = "Not set"
        table.add_row(field, hlt(value))
            
            
    rprint(table)
    option = questionary.select(
        "What do you want to do?",
        choices = [
            "Edit",
            "Exit"
        ]
    ).ask()
    
    if option == "Exit":
        typer.Exit()
    elif option == "Edit":
        path = str(CONFIG_DIR_PATH/ f"{platform}.hackaprofile.conf")
        rprint(f"\n[bold green]Open[/bold green] {path} [bold green]in your preferred editor!")
    
        cbConfirm = questionary.confirm(
            "Do you want to copy path to clipboard?",
            default=False
        ).ask()
        if cbConfirm:
            pyperclip.copy(path)
            rprint("[bold green]✓[/bold green] Copied!")
    
    # with Live(table, refresh_per_second=4):
    #     console.clear()Path(__file__).resolve().parent.parent / "config" / f"{platform}.hackaprofile.conf"
    #     while True:
    #         table.add_row("Status", "I love coding")
    #         # table.add_row("Status")
    #         time.sleep(0.5)
        
@app.command(deprecated=True)
def auth(platform: Annotated[str, typer.Option(prompt=False, help="Which platform you want to authenticate", autocompletion=complete_platform)] = ""):
    """
    Using OAuth to bind HackaProfile to your account
    """
    
    rprint(f"Please use [bold green]hackaprofile setup[/bold green] and select the platforms you want to authorize, use [bold green]--force[/bold green] to re-auth Hackatime")

@app.command()
def revoke(platform: str, all: Annotated[bool, typer.Option("--all")] = False):
    
    # TODO
    if all:
        pass
    else:
        if platform == "hackatime":
            rprint(hackatime.revoke())


def get_agent_pid() -> int:
    """
    Retruns PID of the agent process based on agent.pid
    """

    with open(CONFIG_DIR_PATH / "agent.pid", "r") as f:
        pid = f.readline()
        f.close()
    return int(pid)

def is_agent_alive(pid: int) -> bool:
    return psutil.pid_exists(pid)

@app.command()
def start():
    log = open(Path(__file__).resolve().parent.parent / "logs" / "agent.log", "a")
    sp.Popen(
        [sys.executable, "-u", "agent.py"],
        stdout=log,
        stderr=sp.STDOUT,
        stdin=sp.DEVNULL,
        start_new_session=True
        
    )
    # time.sleep(0.1)
    rprint(f"[bold green]✓[/bold green] Started background worker!")
    
@app.command()
def stop():
    pid = get_agent_pid()
    error = ""
    
    try:
        os.kill(pid, signal.SIGTERM)
    except Exception as e:
        error = " " + str(e)

    time.sleep(0.5)
    if not is_agent_alive(pid) and not error:
        rprint(f"[bold green]✓[/bold green] Stopped background worker!")
    else:
        rprint(f"❌ Worker not stopped{error}. Retry or manually kill process {pid}")


@app.command()
def debug():
    """
    Development purpose only: Uhh, don't worry about it...
    """

    
if __name__ == "__main__":
    app()
