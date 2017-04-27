import pystache
from . import util
from .template import ISSUE_TEMPLATE

def is_archived(card):
    return card["closed"]

def collate_card(card, trello_export):
    actions = (action for action in trello_export["actions"]
        if util.get_deep(action, ("data", "card", "id")) == card["id"])
    actions = (action for action in actions
        if action["type"] == "commentCard")
    return util.merge(card, {
        "actions": tuple(actions)
    })

def read_card_to_issue(full_card, config):
    body = pystache.render(ISSUE_TEMPLATE, {
        "desc": full_card["desc"],
        "url": full_card["url"],
        "actions": full_card["actions"]
    }).strip()

    label_names = (label["name"] for label in full_card["labels"])
    issue_labels = tuple(
        config["remap_labels"][name] for name in label_names
        if config["remap_labels"].get(name)
    )

    return {
        "title": full_card["name"],
        "body": body,
        "labels": issue_labels
    }