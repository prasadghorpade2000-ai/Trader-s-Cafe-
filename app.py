import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- CONFIG ---
CAFE_NAME = "The Trader's Cafe"
ADMIN_PASSWORD = "Prasad@123" 
MENU_FILE = 'menu.csv'
DB_FILE = 'cafe_sales.csv'

st.set_page_config(page_title=CAFE_NAME, layout="wide")

# --- UPDATED MENU DATA (Including Your New Offers) ---
if not os.path.isfile(MENU_FILE):
    new_menu_data = [
        # --- CAFE SPECIAL OFFERS ---
        ['🔥 Cafe Special', 'Classic Burger + Cold Drink + Brownie', 59],
        ['🔥 Cafe Special', 'Pizza (Tom/On/Cap) + Cold Drink + Brownie', 89],
        ['💎 Premium Single', 'Corn Pizza + Cheese Sandwich + Cold Drink', 99],
        ['💎 Premium Single', 'Shezwan Pizza + Cheese Burger + Cold Drink', 119],
        
        # --- STUDENT SPECIALS ---
        ['🎓 Student Special', 'Paneer Piz + Shezwan Piz + Choc Sand + Drink', 189],
        ['🍗 Hunger Killer', '2 Cheese Burger + 1 Mix Veg Pizza', 169],
        ['🎒 Back Benchers', '2 Chz Burg + 2 Veg Piz + 2 Sand + 3 Drinks', 249],
        
        # --- TRADER'S SPECIAL (YOUR THEME) ---
        ['📈 Forex Combo', '2 Paneer Piz + 2 Spicy Salsa + 1 Choc Sand', 299],
        ['📊 Nifty Special', '1 Paneer Piz + 1 Shezwan Piz + 1 Burger + 1 Chz Sand', 239],
        
        # --- REGULAR ITEMS ---
        ['🍕 Pizza', 'Golden Corn', 59],
        ['🍕 Pizza', 'Mighty Paneer', 79],
        ['🍔 Burger', 'Classic Burger', 39],
        ['🥪 Sandwich', 'Grill Sandwich', 39]
    ]
    pd.DataFrame(new_menu_data, columns=['Category', 'Item', 'Price']).to_csv(MENU_FILE, index=False)

menu_df = pd.read_csv(MENU_FILE)

# --- INITIALIZE SESSIONS ---
if 'active_orders' not in st.session_state:
    st.session_state.active_orders = {f"Table {i}": [] for i in range(1, 21)}
if 'current_table' not in st.session_state:
    st.session_state.current_table = "Table 1"

# --- MAIN UI ---
st.title(f"☕ {CAFE_NAME}")
st.caption("Bake Your Taste | Professional Trading Theme Cafe 📈")

# --- TABLE GRID ---
t_cols = st.columns(10)
for i in range(1, 21):
    t_name = f"Table {i}"
    with t_cols[(i-1) % 10]:
        is_occ = len(st.session_state.active_orders[t_name]) > 0
        if st.button(f"{i}\n{'🔴' if is_occ else '🟢'}", key=f"t_{i}", use_container_width=True):
            st.session_state.current_table = t_name

st.divider()

# --- ORDERING SECTION ---
st.subheader(f"📑 Order for {st.session_state.current_table}")
col_menu, col_bill = st.columns()

with col_menu:
    categories = menu_df['Category'].unique()
    tabs = st.tabs(list(categories))
    for i, cat in enumerate(categories):
        with tabs[i]:
            items = menu_df[menu_df['Category'] == cat]
            m_cols = st.columns(2)
            for idx, row in items.iterrows():
                with m_cols[idx % 2]:
                    if st.button(f"{row['Item']}\n₹{row['Price']}", key=f"add_{row['Item']}_{st.session_state.current_table}", use_container_width=True):
                        st.session_state.active_orders[st.session_state.current_table].append({"Item": row['Item'], "Price": row['Price']})
                        st.rerun()

with col_bill:
    st.write("### Current Items")
    curr_items = st.session_state.active_orders[st.session_state.current_table]
    if curr_items:
        total = 0
        for idx, item in enumerate(curr_items):
            c_name, c_del = st.columns()
            c_name.write(f"{item['Item']} (₹{item['Price']})")
            if c_del.button("❌", key=f"del_{st.session_state.current_table}_{idx}"):
                st.session_state.active_orders[st.session_state.current_table].pop(idx)
                st.rerun()
            total += item['Price']
        
        st.divider()
        st.subheader(f"Total: ₹{total}")
        phone = st.text_input("WhatsApp Number", value="91")
        
        if st.button("✅ Complete & Send WhatsApp", type="primary", use_container_width=True):
            # WhatsApp Logic
            items_txt = "\n".join([f"- {i['Item']}" for i in curr_items])
            wa_msg = f"*{CAFE_NAME}* ☕\n\n*Order:* \n{items_txt}\n\n*Grand Total: ₹{total}*\n\n📈 Happy Trading!"
            wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(wa_msg)}"
            
            st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:5px; font-weight:bold;">📲 Send Bill</button></a>', unsafe_allow_html=True)
            st.session_state.active_orders[st.session_state.current_table] = []
    else:
        st.info("Table is empty. Select items to start.")
