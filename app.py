import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import altair as alt
from backend import (
    get_all_items,
    get_item_data,
    format_gold,
    create_all_items_file,
    load_tracked_item_ids,
    save_tracked_item_ids
)
from purchase_tracker import add_purchase, get_item_total, edit_purchase, delete_purchase

# Auto-refresh every 160 seconds
st_autorefresh(interval=160 * 1000, key="data_refresh")

st.set_page_config(page_title="GW2 Trading Post Dashboard", layout="wide")
st.title("Guild Wars 2 Trading Post Dashboard")

# Load item IDs
ITEM_IDS = load_tracked_item_ids()
all_items = get_all_items()

# Top-of-page item search and add
st.subheader("Add New Tracked Item")
search_query = st.text_input("Search item by name")

if search_query:
    matches = [item for item in all_items if search_query.lower() in item["name"].lower()]
    if matches:
        selected_item = st.selectbox(
            "Select an item to track", matches, format_func=lambda x: x["name"]
        )
        if st.button("Add Item"):
            if selected_item["id"] not in ITEM_IDS:
                ITEM_IDS.append(selected_item["id"])
                save_tracked_item_ids(ITEM_IDS)
                st.rerun()
    else:
        st.write("No matches found.")

# Refresh all items list
if st.button("Refresh Item List"):
    create_all_items_file()
    st.rerun()

# Main item display
for item_id in ITEM_IDS:
    data = get_item_data(item_id)
    with st.container():
        st.image(data["icon"], width=50)
        st.markdown(f"### {data['name']}")
        st.metric(label="Buy Price", value=format_gold(data["buy"]))
        st.metric(label="Sell Price", value=format_gold(data["sell"]))

        if st.button("Remove Item", key=f"remove_{item_id}"):
            ITEM_IDS.remove(item_id)
            save_tracked_item_ids(ITEM_IDS)
            st.rerun()

        st.markdown("---")
        st.markdown("**Add Purchase**")
        qty = st.number_input(f"Quantity {item_id}", min_value=1, step=1, key=f"qty_{item_id}")
        price = st.number_input(f"Price per item {item_id} (in gold)", min_value=0.0, format="%.2f", key=f"price_{item_id}")
        if st.button("Save Purchase", key=f"save_{item_id}"):
            add_purchase(item_id, qty, price)
            st.success("Saved!")

        st.markdown("**Edit/Delete Purchases**")
        purchases = get_item_total(item_id, full=True)
        for index, p in enumerate(purchases):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                new_qty = st.number_input(f"Qty #{index}", value=p["quantity"], key=f"edit_qty_{item_id}_{index}")
            with col2:
                new_price = st.number_input(f"Price #{index}", value=p["price"], format="%.2f", key=f"edit_price_{item_id}_{index}")
            with col3:
                if st.button("Update", key=f"update_{item_id}_{index}"):
                    edit_purchase(item_id, index, new_qty, new_price)
                    st.success("Updated!")
                    st.rerun()
                if st.button("Delete", key=f"delete_{item_id}_{index}"):
                    delete_purchase(item_id, index)
                    st.success("Deleted!")
                    st.rerun()

        st.markdown("**Your Holdings**")
        total_qty, avg_price = get_item_total(item_id)
        st.text(f"Owned: {total_qty} at avg {format_gold(avg_price)}")

        if total_qty > 0:
            value_now = total_qty * data["sell"] * 0.85
            cost_basis = total_qty * avg_price
            profit = value_now - cost_basis
            profit_color = "green" if profit >= 0 else "red"
            st.markdown(f"**Profit/Loss:** :{profit_color}[{format_gold(profit)}]")

        st.markdown("---")

# Profit Summary Table and Chart
st.header("Portfolio Summary")
id_to_name = {item["id"]: item["name"] for item in all_items}

summary_data = []
for item_id in ITEM_IDS:
    item_info = get_item_data(item_id)
    total_qty, avg_price = get_item_total(item_id)
    if total_qty == 0:
        continue
    current_price = item_info["sell"] * 0.85  # account for 15% TP fee
    profit = (current_price - avg_price) * total_qty
    summary_data.append({
        "Item": id_to_name.get(item_id, f"ID {item_id}"),
        "Quantity": total_qty,
        "Avg Price": avg_price,
        "Current TP Price": current_price,
        "Profit": profit
    })

if summary_data:
    df = pd.DataFrame(summary_data)
    df["Profit"] = df["Profit"].round(2)
    df["Current TP Price"] = df["Current TP Price"].round(2)
    df["Avg Price"] = df["Avg Price"].round(2)
    st.dataframe(df)

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("Item", sort="-y"),
        y="Profit",
        color=alt.condition(alt.datum.Profit >= 0, alt.value("green"), alt.value("red"))
    ).properties(title="Profit/Loss by Item", width=600)

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No data to display in profit summary.")
