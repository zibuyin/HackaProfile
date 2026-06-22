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

### Setup
If you are deploying on a headless device (e.g. a VPS connected via ssh), use:
```bash
hackaprofile setup --headless
```
If you are deploying on your personal device, use:
```bash
hackaprofile setup --headless
```
> [!TIP]
> No matter which setup you use, the Hackatime data source will be from the computer you are typing from.
> If you deployed this on a VPS, but you are coding on your PC and Hackatime is installed on it, the data source will be from your PC

Then follow the guided setup

### Usage
Configure profile messages via `hackaprofile config [platform name e.g. slack]`.
within the config file, you will see something like this:
```env
# title = 
# phone = 
# real_name =
# display_name = 
```
Uncomment the values you want to set, e.g:
```
# title = 
# phone = 
#real_name =
display_name = 
```
Now you can set the value of this field (which corrosponds to the fields on Slack/the platform you are configuring). There are some useful placeholders and logic operators you could use (see below)
```
# title = 
# phone = 
#real_name =
display_name = Bob {% if language %}(Typing {{language}}...){% elif editor == "Slack" %}(Yapping on Slack) {% endif %}
```

Due to API rate limiting, there will be a ~20s delay between changing tasks (e.g. changing to a new language) and the status updating, this delay *could* be reduced by reducing the `interval` value in `hackaprofile.conf` (#TODO). However, doing so you are risking getting rate-limited. Find a balance.

You could refresh and see the new config in action by running `hackaprofile restart` - which restarts the background worker

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