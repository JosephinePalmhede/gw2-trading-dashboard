# This module handles loading and saving tracked purchases
import json
import os

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {}

def save_portfolio(data):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_purchase(item_id, quantity, price):
    data = load_portfolio()
    item_id_str = str(item_id)
    if item_id_str not in data:
        data[item_id_str] = []
    data[item_id_str].append({"quantity": quantity, "price": price})
    save_portfolio(data)

# Use an index to handle when a single item has more than one purchase
def edit_purchase(item_id, index, new_qty, new_price):
    portfolio = load_portfolio()
    item = str(item_id)
    if item in portfolio and 0 <= index < len(portfolio[item]):
        portfolio[item][index]["quantity"] = new_qty
        portfolio[item][index]["price"] = new_price
        save_portfolio(portfolio)

def delete_purchase(item_id, index):
    portfolio = load_portfolio()
    item = str(item_id)
    if item in portfolio and 0 <= index < len(portfolio[item]):
        portfolio[item].pop(index)
        # if there are no purchases of the item remaining, remove it
        if not portfolio[item]:
            del portfolio[item]
        save_portfolio(portfolio)

def get_item_total(item_id, full=False):
    all_data = load_all_purchases()
    purchases = all_data.get(str(item_id), [])
    
    if full:
        return purchases

    if not purchases:
        return 0, 0.0
    
    total_quantity = sum(p["quantity"] for p in purchases)
    total_cost = sum(p["quantity"] * p["price"] for p in purchases)
    avg_price = total_cost / total_quantity if total_quantity > 0 else 0.0
    return total_quantity, avg_price

def load_all_purchases():
    return load_portfolio()
