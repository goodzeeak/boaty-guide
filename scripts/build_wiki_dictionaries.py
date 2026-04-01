#!/usr/bin/env python3
"""
Build offline OSRS Wiki-backed dictionaries for parser normalization.

Outputs:
  data/wiki/quests.json
  data/wiki/npcs.json
  data/wiki/items.json
  data/wiki/locations.json
"""

import json
import os
from collections import OrderedDict
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://oldschool.runescape.wiki/api.php"
CATEGORY_MAP = {
    "quests": "Category:Quests",
    "npcs": "Category:Non-player_characters",
    "items": "Category:Items",
    "locations": "Category:Locations",
}


def api_request(params):
    query = urlencode(params)
    request = Request(
        f"{API_URL}?{query}",
        headers={"User-Agent": "BoatyGuideDictionaryBuilder/1.0"},
    )
    with urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_category_titles(category_title):
    titles = []
    cmcontinue = None

    while True:
        params = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": category_title,
            "cmnamespace": 0,
            "cmlimit": "500",
            "cmtype": "page",
        }
        if cmcontinue:
            params["cmcontinue"] = cmcontinue

        payload = api_request(params)
        titles.extend(member["title"] for member in payload.get("query", {}).get("categorymembers", []))
        cmcontinue = payload.get("continue", {}).get("cmcontinue")
        if not cmcontinue:
            break

    return ordered_unique(filter_titles(titles))


def filter_titles(titles):
    filtered = []
    for title in titles:
        if not title:
            continue
        if title.startswith(("File:", "Template:", "Module:", "User:", "Transcript:")):
            continue
        if title.endswith(("/Quick guide", "/Strategies")):
            continue
        filtered.append(title)
    return filtered


def ordered_unique(values):
    return list(OrderedDict.fromkeys(values))


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    wiki_dir = os.path.join(project_dir, "data", "wiki")
    os.makedirs(wiki_dir, exist_ok=True)

    for output_name, category_title in CATEGORY_MAP.items():
        titles = fetch_category_titles(category_title)
        output_path = os.path.join(wiki_dir, f"{output_name}.json")
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(titles, handle, indent=2, ensure_ascii=False)
        print(f"Wrote {len(titles)} entries to {output_path}")


if __name__ == "__main__":
    main()
