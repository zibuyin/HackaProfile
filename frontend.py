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
# from rich.terminal_theme import MONOKAI

import typer
from typing import Annotated

import backend

import questionary

import os


console = Console()

app = typer.Typer(no_args_is_help=True)
hackatime = backend.hackatime()
slack = backend.slack()

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
        
        
        
@app.command()
def config(platform: Annotated[str, typer.Argument]):
    table = Table(
        "Field",
        "Value",
        title="Preview Slack",
        box=box.ROUNDED,
        expand=True,
    )
    

    profile_fields = slack.get_team_profile()["profile"]["fields"]
    profile_id_kv= {}
    for profile_field in profile_fields:
        try:
            if not profile_field['permissions']["api"]:
                # print(profile_field['permissions'])
                fieldEditable = True
            else:
                # print(profile_field['permissions'])
                fieldEditable = False
            apiPerms = profile_field['permissions']["api"]
        except KeyError:
            fieldEditable = False
            apiPerms = "None"
        
        if fieldEditable:
            profile_field["id"] = profile_field["label"]

        # rprint(profile_id_value_pair)
    
    profile = slack.get_profile()["profile"]
    # rprint(profile)
    normalized_kv = {}
    for field in profile:
        # print((type(field), type(profile[field])))
        value = profile[field]
        if field == "fields":
            labels = profile[field]
            # print(labels)
            keys = list(labels.keys())
            values = list(labels.values())
            # print((keys, values))
            
            for i in range(len(keys) - 1):
                key = profile_id_kv.get(keys[i], "Unknown")
                normalized_kv[key] = values[i]["value"]
        else:
            normalized_kv[field] = value
    
    # normalized_kv.pop("status_emoji_display_info")
    rprint(normalized_kv)
    
    # for row in normalized_kv:
    kv_keys = list(normalized_kv.keys())
    kv_values = list(normalized_kv.values())
    
    for i in range(len(kv_keys) - 1):
        # rprint((type(field), type(value)))
        rprint((kv_keys[i], kv_values[i]))
        table.add_row(kv_keys[i], str(kv_values[i]))
        
    
        # table.add_row(field)
    # panel = Panel(table)
    # console.clear()
    rprint(table)
    rprint("\n")
    
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

