import json
import os

from src.settings import DATA_FOLDER


def create_rules_file(rules):
    """
    Save rules contents to a JSON file.
    Normally, instead of storing to a local file system, we put the files in
    some cloud storage for shared access across pipelines/users.
    """
    file_path = os.path.join(DATA_FOLDER, "rules", f"{rules['name']}.json")
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as json_file:
        json.dump(rules, json_file)
