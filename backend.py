# backend.py
import requests
import json
import os

ITEMS_FILE = "tracked_items.json"
ALL_ITEMS_FILE = "all_items.json"

# Save a slimmed down version of all items (id + name) to all_items file
def create_all_items_file():
    tradable_response = requests.get("https://api.guildwars2.com/v2/commerce/prices")
    tradable_ids = set(tradable_response.json())

    ids_response = requests.get("https://api.guildwars2.com/v2/items")
    item_ids = ids_response.json()

    all_items = []
    for i in range(0, len(item_ids), 200):
        batch = item_ids[i:i+200]
        ids_str = ",".join(map(str, batch))
        info_response = requests.get(f"https://api.guildwars2.com/v2/items?ids={ids_str}")
        items = info_response.json()
        all_items.extend({"id": item["id"], "name": item["name"]}
                         for item in items if "name" in item and item["id"] in tradable_ids)

    with open(ALL_ITEMS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_items, f)


def get_all_items():
    if not os.path.exists(ALL_ITEMS_FILE):
        create_all_items_file()
    with open(ALL_ITEMS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_tracked_item_ids():
    if os.path.exists(ITEMS_FILE):
        with open(ITEMS_FILE, "r") as f:
            return json.load(f)
    return [19721, 24277, 43773]


def save_tracked_item_ids(item_ids):
    with open(ITEMS_FILE, "w") as f:
        json.dump(item_ids, f)


def get_item_data(item_id):
    info_url = f"https://api.guildwars2.com/v2/items/{item_id}"
    price_url = f"https://api.guildwars2.com/v2/commerce/prices/{item_id}"

    info = requests.get(info_url).json()
    price = requests.get(price_url).json()

    return {
        "id": item_id,
        "name": info.get("name", "Unknown"),
        "icon": info.get("icon"),
        "buy": price["buys"]["unit_price"] / 100,
        "sell": price["sells"]["unit_price"] / 100
    }


def format_gold(value):
    total_copper = int(round(value * 100))
    gold = total_copper // 10000
    silver = (total_copper % 10000) // 100
    copper = total_copper % 100
    return f"{gold}g {silver}s {copper}c"


def gold_to_float(price: float) -> tuple[int, int, int]:
    gold = int(price)
    silver = int((price * 100) % 100)
    copper = int((price * 10000) % 100)
    return gold, silver, copper


def float_to_gold(gold: int, silver: int, copper: int) -> float:
    return gold + silver / 100 + copper / 10000
