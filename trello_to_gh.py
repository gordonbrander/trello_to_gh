#!/usr/bin/env python3
import json
import argparse
from trello_to_gh import util
from trello_to_gh import trello
from os import path, makedirs

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
    '--cache_dir', "-d",
    help="Path to cache dir",
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

    list_id_by_name = {x["name"]: x["id"] for x in trello_export["lists"]}
    label_id_by_name = {x["name"]: x["id"] for x in trello_export["labels"]}

    exclude_list_ids = frozenset(
        list_id_by_name[name]
        for name in config["exclude_with_list"]
    )

    exclude_label_ids = frozenset(
        label_id_by_name[name]
        for name in config["exclude_with_label"]
    )

    cards = trello_export["cards"]

    # Filter out archived
    cards = (card for card in cards
        if not trello.is_archived(card))

    # Filter out excluded lists
    cards = tuple(
        card for card in cards
        if card["idList"] not in exclude_list_ids)

    # Filter out excluded labels
    cards = (
        card for card in cards
        if frozenset(card["idLabels"]).isdisjoint(exclude_label_ids)
    )

    cards_full = (trello.collate_card(card, trello_export) for card in cards)

    # Read cards
    issues = (trello.read_card_to_issue(card, config) for card in cards_full)

    for issue in issues:
        file_title = util.safe_filename(issue["title"])
        file_name = "{}.json".format(file_title)
        with open(path.join(issues_cache_dir, file_name), "w") as f:
            json.dump(issue, f)