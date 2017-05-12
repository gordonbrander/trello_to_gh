#!/usr/bin/env python3
import json
import argparse
from trello_to_gh import util
from trello_to_gh import trello
from os import path, makedirs
import logging

parser = argparse.ArgumentParser(
    description="""A lettersmith plugin.""",
)
parser.add_argument(
    'export_file',
    help="Path to Trello .json export file",
    type=util.read_json
)

parser.add_argument(
    '--config_file', '-c',
    help="Path to configuration .json file (defaults to config.json)",
    type=util.read_json,
    default="config.json"
)

parser.add_argument(
    '--credentials_file', '-p',
    help="Path to credentials .json file that contains oauth token (defaults to credentials.json)",
    type=util.read_json,
    default="credentials.json"
)

parser.add_argument(
    '--cache_dir', "-d",
    help="Path to cache dir (defaults to \"cache\")",
    type=str,
    default="cache"
)

parser.add_argument(
    '--dry_run',
    help="Run script without publishing to GitHub",
    action="store_true"
)
parser.set_defaults(dry_run=False)

if __name__ == "__main__":
    args = parser.parse_args()
    trello_export = args.export_file
    config = args.config_file
    cache_dir = args.cache_dir

    # Make sure cache dir exists
    issues_cache_dir = path.join(cache_dir, "issues_json")
    try:
        makedirs(issues_cache_dir)
    except FileExistsError:
        pass

    issues = trello.collate_issues(trello_export, config)

    for issue in issues:
        file_title = util.safe_filename(issue["title"])
        file_name = "{}.json".format(file_title)
        with open(path.join(issues_cache_dir, file_name), "w") as f:
            json.dump(issue, f)