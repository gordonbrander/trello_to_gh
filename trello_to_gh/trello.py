import pystache
from . import util
from .template import ISSUE_TEMPLATE
from itertools import chain

def is_archived(card):
    return card["closed"]

def collate_card(card, trello_export):
    actions = (
        action for action in trello_export["actions"]
        if action["type"] == "commentCard" and
        util.get_deep(action, ("data", "card", "id")) == card["id"]
    )

    list_name = next((
        l["name"] for l in trello_export["lists"]
        if l["id"] == card["idList"]
    ), "")

    return util.merge(card, {
        "nameList": list_name,
        "actions": tuple(actions)
    })

def read_card_to_issue(full_card, config):
    body = pystache.render(ISSUE_TEMPLATE, {
        "desc": full_card["desc"],
        "url": full_card["url"],
        "actions": full_card["actions"]
    }).strip()

    add_labels = config.get("add_labels", [])
    labels_map = config.get("remap_labels", {})
    lists_map = config.get("remap_lists", {})

    label_names = tuple(label["name"] for label in full_card["labels"])
    list_name = full_card["nameList"]

    labels_to_labels = chain.from_iterable(
        labels_map.get(name, [])
        for name in label_names
    )

    list_to_labels = util.get_deep(lists_map, (list_name, "labels"), [])
    list_to_milestone = util.get_deep(lists_map, (list_name, "milestone"), None)
    list_to_state = util.get_deep(lists_map, (list_name, "state"), "open")

    all_labels = tuple(chain(
        labels_to_labels,
        list_to_labels,
        add_labels
    ))

    return {
        "title": full_card["name"],
        "body": body,
        "labels": all_labels,
        "milestone": list_to_milestone,
        "state": list_to_state
    }

def collate_issues(trello_export, config):
    """
    Given a `trello_export` json structure and a `config` json structure,
    return an iterable dicts suitable for serializing as GH issue JSON blobs.
    """
    exclude_with_list = config.get("exclude_with_list", [])
    exclude_list_ids = frozenset(
        trello_list["id"]
        for trello_list in trello_export["lists"]
        if trello_list["name"] in exclude_with_list)

    exclude_with_label = config.get("exclude_with_label", [])
    exclude_label_ids = frozenset(
        trello_label["id"]
        for trello_label in trello_export["labels"]
        if trello_label["name"] in exclude_with_label)

    cards = trello_export["cards"]

    # Filter out archived
    cards = (card for card in cards
        if not is_archived(card))

    # Filter out excluded lists
    cards = tuple(
        card for card in cards
        if card["idList"] not in exclude_list_ids)

    # Filter out excluded labels
    cards = (
        card for card in cards
        if frozenset(card["idLabels"]).isdisjoint(exclude_label_ids)
    )

    # This collates all of the information assocated with the card...
    # associating list names with IDs, that kind of thing.
    cards_full = (collate_card(card, trello_export) for card in cards)

    # Read cards as issues
    issues = (read_card_to_issue(card, config) for card in cards_full)
    return issues