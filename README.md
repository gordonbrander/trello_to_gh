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

The script assumes two configuration files:

- `config.json` contains the Github-to-Trello configuration (can be customized via `--config_file` flag)
- `credentials.json` contains a GitHub OAuth token for communicating with GitHub's API.

The script assumes you have a `config.json` file in the same directory as the
script.

### config.json

Example `config.json` file:

```json
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
  "add_labels": ["from-trello"],
  "remap_labels": {
    "UI": ["ui"],
    "Cloud": ["cloud"],
    "Backend": ["backend"],
    "Hardware": ["hardware"],
    "Manufacturing": ["hardware"],
    "Mech Support": ["hardware"],
    "Computer Vision / ML": ["cv"]
  }
}
```

### credentials.json

This script uses an OAuth token to autheticate with the GitHub API. This will
increase the rate limit to 5000 (meaning you can POST up to 5000 issues before
GitHub will give you a time-out).

To use the `publish` action, you're required to create a credentials JSON file
(by default `credentials.json`) with the following content:

Example:

```json
{
  "oauth_token": "YOUR_OAUTH_TOKEN_HERE"
}
```

You can get an OAuth token here: https://github.com/settings/tokens/new. The
only priviledges this script needs are the `repo` privileges. Check those,
generate a token, and you're good to go!

## Editing before Publishing

By default the script will load what has been read from the export file into the
cache directory and then publish everything in the cache directory to GitHub.

If you want to do a dry run or prune the issues before publishing, you can
run this script with `--actions load_cache`. This will create a cache full
of .json files that you can edit.

To publish a pruned list, without overwriting the changes you've made,
run the script again with `--actions publish`. This will publish anything
found in the cache directory, without first writing to the cache directory.

To do it all in one go, either omit the `actions` flag, or specify `--actions load_cache publish`.

## Retrying After Hitting Rate-Limit

Most users shouldn't hit this case, since GitHub will allow up to 5000 issues to be created in one go. In the rare chance that you have more than 5000 issues to publish, the script has a workaround for starting a new request where you last left off.

After successfully publishing an issue, the script will move the issue's cache file from the cache `queue` directory to the cache `published` directory. This means when a rate-limit causes the script to fail, the queue folder will contain just the files that haven't yet been published.

You can start publishing where you left off by specifying ONLY the `publish` flag and OMITTING the `load_cache` flag (`--actions publish`).

## Other Tools

You might also want to take a look at these other tools:

- https://github.com/RickyCook/import-trello-github