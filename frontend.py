import time
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console
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

import backend

import questionary

import os

import dotenv
console = Console()

app = typer.Typer(no_args_is_help=True)
hackatime = backend.hackatime()
slack = backend.slack()
slack_config = dotenv.dotenv_values("config/slack.hackaprofile.conf")

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
    rprint("status")


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
    
    # If no token stored
    if force or not hackatime.status()["ok"]:
        # hackatimeConfirm = Confirm.ask("[bold cyan]Do you want to authorize Hackatime (This will redirect you to OAuth page)", default=True)
        hackatimeConfirm  = questionary.confirm("Do you want to authorize Hackatime (This will redirect you to OAuth page)").ask()
        if hackatimeConfirm:
            with console.status("Authorizing Hackatime", spinner="dots"):
                ok, hackatime_token = hackatime.authorize()
                
            if ok:
                rprint("[bold green]✓[/bold green] Hackatime authorized!")
                
            else:
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
    slack_config_keys = list(slack_config.keys())
    slack_config_values = list(slack_config.values())
    
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
        path = f"{os.getcwd()}/config/{platform}.hackaprofile.conf"
        rprint(f"\n[bold green]Open[/bold green] {path} [bold green]in your preferred editor!")
    # with Live(table, refresh_per_second=4):
    #     console.clear()
    #     while True:
    #         table.add_row("Status", "I love coding")
    #         # table.add_row("Status")
    #         time.sleep(0.5)
        
@app.command()
def auth(platform: Annotated[str, typer.Option(prompt=True, help="Which platform you want to authenticate", autocompletion=complete_platform)]):
    """
    Using OAuth to bind HackaProfile to your account
    """
    
    rprint(f"auth {platform}")
    
@app.command()
def debug():
    """
    Development purpose only: Uhh, don't worry about it...
    """
    json = slack.get_profile()
    rprint(json)

    
if __name__ == "__main__":
    app()

