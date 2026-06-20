# HackaProfile
<img src="./assets/icon.png" width=30% alt="HackaProfile logo"></img>

### A simple tool to automatically update Slack (more platforms *SOON*) user profile based on their Hackatime/Wakatime heartbeat!

## Features
- FULLY local (no data leaves your device except for the API calls to update profile)
- FULLY customizable (see the Place holder variables section)
- More features #TODO ~~(I don't wanna write README.md >:3)~~

## installation
> [!TIP]
> One line install does not work yet!
### MacOS
`brew install hackaprofile`
### Linux
Debian/Ubuntu:
`apt install hackaprofile`

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

