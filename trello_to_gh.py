#!/usr/bin/env python3
import json
import argparse
from trello_to_gh import util
from trello_to_gh import trello
import os
from os import path
import logging
import requests

parser = argparse.ArgumentParser(
    description="""Publish GitHub issues from a Trello .json export file.""",
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

LOAD_CACHE = "load_cache"
PUBLISH = "publish"
DEFAULT_ACTIONS = (LOAD_CACHE, PUBLISH,)

parser.add_argument(
    '--actions',
    help="""A space-separated list of actions to perform.

By default the script will load what has been read from the export file into the
cache directory and then publish everything in the cache directory to GitHub.

If you want to do a dry run or prune the issues before publishing, you can
run this script with ``--actions load_cache``. This will create a cache full
of .json files that you can edit.

To publish a pruned list, without overwriting the changes you've made,
run the script again with ``--actions publish``. This will publish anything
found in the cache directory, without first writing to the cache directory.
""",
    choices=DEFAULT_ACTIONS,
    default=DEFAULT_ACTIONS,
    nargs='+'
)

if __name__ == "__main__":
    args = parser.parse_args()
    trello_export = args.export_file
    config = args.config_file
    credentials = args.credentials_file
    cache_dir = args.cache_dir
    # Make sure cache dir exists
    issues_queue = path.join(cache_dir, "queue")
    issues_published = path.join(cache_dir, "published")
    issues_url = "https://api.github.com/repos/{owner}/{repo}/issues".format(
        owner=config["github"]["owner"],
        repo=config["github"]["repo"])

    try:
        os.makedirs(issues_queue)
    except FileExistsError:
        pass

    try:
        os.makedirs(issues_published)
    except FileExistsError:
        pass

    if LOAD_CACHE in args.actions:
        issues = trello.collate_issues(trello_export, config)

        for issue in issues:
            file_title = util.safe_filename(issue["title"])
            file_name = "{}.json".format(file_title)
            with open(path.join(issues_queue, file_name), "w") as f:
                json.dump(issue, f)

    if PUBLISH in args.actions:
        # See https://developer.github.com/v3/#authentication
        params = {"access_token": credentials["oauth_token"]}
        file_paths = (
            path.join(issues_queue, file_path)
            for file_path in os.listdir(issues_queue)
            if file_path.endswith(".json"))
        issues = (
            (file_path, util.read_json(file_path))
            for file_path in file_paths)
        for file_path, issue in issues:
            resp = requests.post(issues_url, json=issue, params=params)
            if resp.status_code == 201:
                # On success, move file to published dir
                os.rename(
                    file_path,
                    path.join(issues_published, path.basename(file_path))
                )
                # And log success
                resp_json = resp.json()
                log = json.dumps({
                    "url": resp_json["url"],
                    "id": resp_json["id"]
                })
                logging.info(log)
            else:
                logging.error(resp.text)