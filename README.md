# trello_to_gh

WORK IN PROGRESS

A quick-and-dirty script to convert Trello's export JSON file into GitHub Issues, and publish them to Github.

## Installing

    pip install -r requirements.txt

## Using

    trello_to_gh.py path/to/trello_export.json

Help:

    trello_to_gh.py --help

## Configuring

The script assumes you have a `config.json` file in the same directory as the
script.

```json

Example config file.

{
  "exclude_with_list": [
    "Done",
    "Global Timeline",
    "Meetings",
    "Meeting Notes"
  ],
  "exclude_with_label": [
    "Admin",
    "Bizdev",
    "Hiring/Recruiting",
    "Meeting",
    "Operations",
    "RFC",
    "Community / Communications"
  ],
  "remap_labels": {
    "UI": "ui",
    "Cloud": "cloud",
    "Backend": "backend",
    "Hardware": "hardware",
    "Manufacturing": "hardware",
    "Mech Support": "hardware",
    "Computer Vision / ML": "cv"
  }
}
```