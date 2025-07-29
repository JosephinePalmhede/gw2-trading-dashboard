import pandas as pd
import altair as alt
import json
import os
from backend import get_all_items, get_item_data
from purchase_tracker import get_item_total

# Load all purchases
PURCHASES_FILE = "portfolio.json"

# Load purchase data
with open(PURCHASES_FILE, "r") as f:
    purchase_data = json.load(f)

# Convert to flat list for pandas DataFrame
rows = []
all_items = get_all_items()
id_to_name = {item["id"]: item["name"] for item in all_items} # dictionary that maps an item's id to its name

for item_id_str, purchases in purchase_data.items():
    item_id = int(item_id_str)
    item_name = id_to_name.get(item_id, f"ID {item_id}")
    market_data = get_item_data(item_id)
    current_sell = market_data["sell"]

    total_qty, avg_price = get_item_total(item_id)
    if total_qty == 0:
        continue

    cost_basis = total_qty * avg_price
    market_value = total_qty * current_sell * 0.85
    profit = market_value - cost_basis

    rows.append({
        "Item": item_name,
        "Quantity": total_qty,
        "Avg Purchase Price (g)": avg_price,
        "Current Sell Price (g)": current_sell,
        "Total Profit (g)": profit
    })

# Create DataFrame
summary_df = pd.DataFrame(rows)

# Show table (if using with Streamlit UI)
# st.dataframe(summary_df)

# Create bar chart with Altair
chart = alt.Chart(summary_df).mark_bar().encode(
    x=alt.X("Item", sort="-y", title="Item"),
    y=alt.Y("Total Profit (g)", title="Profit (gold)"),
    color=alt.condition(
        alt.datum['Total Profit (g)'] > 0,
        alt.value("green"),
        alt.value("red")
    ),
    tooltip=["Item", "Total Profit (g)", "Quantity", "Avg Purchase Price (g)", "Current Sell Price (g)"]
).properties(
    title="Profit/Loss per Tracked Item",
    width=800,
    height=400
)

# If in Streamlit:
# import streamlit as st
# st.altair_chart(chart, use_container_width=True)

# For use as module:
def get_profit_chart():
    return chart

def get_profit_table():
    return summary_df
