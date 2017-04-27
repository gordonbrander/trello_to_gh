import json

def merge(d, patch):
    out = d.copy()
    out.update(patch)
    return out

def read_json(json_file_path):
    with open(json_file_path, "r") as f:
        return json.load(f)

def get_deep(d, keys, default=None):
    try:
        for key in keys:
            d = d[key]
        return d
    except KeyError:
        return default

def safe_filename(text):
    return (
        text
            .strip()
            .replace(";", "")
            .replace(":", "")
            .replace("/", "")
    )