# HackaProfile
<img src="./assets/icon.png" width=30% alt="HackaProfile logo"></img>

### A simple tool to automatically update Slack (more platforms *SOON*) user profile based on their Hackatime/Wakatime heartbeat!

## Features
- FULLY local (no data leaves your device except for the API calls to update profile)
- FULLY customizable (see the Place holder variables section)
- More features #TODO ~~(I don't wanna write README.md >:3)~~

## installation
### Install pipx
Check [pipx docs](https://pipx.pypa.io/stable/how-to/install-pipx/)

### Install Hackaprofile
```bash
pipx install hackaprofile
hackaprofile setup
```

Then follow the guided setup

## Placeholder Variables
A key feature of HackaProfile is that it allows you to customise your profile however you like (just like how you would change it on Slack/other platforms) BUT it **also allows you to use dynamic values** (i.e. Placeholder variables).

Example
`I am typing {{language}} in {{project}} project` becomes `I am typing Python in HackaProfile project`

-`{{id}}` Some sort of Hackatime id, might be unique?
- `{{created_at}}` When was the Hackatime data last fetched
- `{{time}}` Current time in Unix Timestamp
- `{{category}}`: Category of the Hackatime action
    - communicating
    - ai coding
    - coding
    - writing docs
- `{{project}}` Hackatime project name
- `{{language}}` Shows the current language that that you are working on
- `{{editor}}` Current IDE/Editor
- `{{operating_system}}` The current OS (N.B for MacOS, it shows `darwin`)
- `{{entity}}` Path to the file workng on
- `{{machine}}` Current machine's hostname

## Logic Operators
You could not only dynamically set variables, but you could also **choose how they are represented dynamically*

### If Statements:
`{% if [condition] %} ... {% elif [condition] %} ... {% else %} ... {% endif %}
### Filters:

Transforms the string to lowercase
```
{{string|lower}}
```

Transforms the STRING to UPPERCASE
```
{{string|upper}}
```

Transforms the String into a Title format
```
{{string|title}}
```

### Escaping:
```
{{ "string to be escaped" }}
```
or
```
{% raw %}
string to be escaped
{% endraw %}
```