import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- 1. CONFIGURATION & THEME ---
CAFE_NAME = "The Trader's Cafe"
TAGLINE = "Bake Your Taste | Profit in Every Bite 📈"
ADMIN_PASSWORD = "Prasad@123"
MENU_FILE = 'menu_data.csv'
DB_FILE = 'cafe_sales.csv'
INFO_FILE = 'cafe_info.csv'

st.set_page_config(page_title=CAFE_NAME, layout="wide")

# Custom Trading Theme (Dark Mode)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { border-radius: 10px; font-weight: bold; transition: 0.3s; height: 60px; width: 100%; }
    div[data-testid="stMetricValue"] { color: #00ff41; }
    .insta-btn { background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #bc1888); color: white !important; padding: 10px; border-radius: 8px; text-align: center; display: block; text-decoration: none; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
if not os.path.isfile(MENU_FILE):
    pd.DataFrame([
        ['🎂 Cakes', 'Chocolate Dutch', 350], ['🎂 Cakes', 'Red Velvet', 450],
        ['🍕 Pizza', 'Forex Special', 199], ['🍔 Burger', 'Nifty Classic', 89],
        ['🔥 Special', '1 Burger + 1 Drink + Brownie', 59]
    ], columns=['Category', 'Item', 'Price']).to_csv(MENU_FILE, index=False)

if not os.path.isfile(DB_FILE):
    pd.DataFrame(columns=['Date', 'Table', 'Total', 'Method', 'Status', 'Customer']).to_csv(DB_FILE, index=False)

if not os.path.isfile(INFO_FILE):
    pd.DataFrame([['Sangli, MH', '9100000000', 'the_trader_cafe']], columns=['Address', 'Contact', 'Insta']).to_csv(INFO_FILE, index=False)

menu_df = pd.read_csv(MENU_FILE)
info_df = pd.read_csv(INFO_FILE)

# --- 3. SESSION STATE ---
if 'active_orders' not in st.session_state:
    st.session_state.active_orders = {f"Table {i}": [] for i in range(1, 21)}
if 'current_table' not in st.session_state:
    st.session_state.current_table = "Table 1"

# --- 4. SIDEBAR: ADMIN & SETTINGS ---
st.sidebar.title("🔐 Admin Panel")
pwd = st.sidebar.text_input("Password", type="password")

if pwd == ADMIN_PASSWORD:
    choice = st.sidebar.radio("Menu:", ["Sales Report", "Edit Menu/Rates", "Cafe Info"])
    
    if choice == "Edit Menu/Rates":
        st.sidebar.subheader("Manage Items")
        edited_menu = st.data_editor(menu_df, num_rows="dynamic")
        if st.sidebar.button("Save Menu"):
            edited_menu.to_csv(MENU_FILE, index=False)
            st.rerun()
            
    if choice == "Sales Report":
        sales_df = pd.read_csv(DB_FILE)
        st.sidebar.metric("Today's Sale", f"₹{sales_df['Total'].sum()}")
        st.sidebar.download_button("Download Report", sales_df.to_csv(), "sales.csv")

# --- 5. MAIN UI: TABLE TRACKER ---
st.title(f"📈 {CAFE_NAME}")
st.caption(TAGLINE)

t_cols = st.columns(10)
for i in range(1, 21):
    t_name = f"Table {i}"
    with t_cols[(i-1)%10]:
        is_occ = len(st.session_state.active_orders[t_name]) > 0
        color = "🔴" if is_occ else "🟢"
        if st.button(f"{i}\n{color}", key=f"t_{i}"):
            st.session_state.current_table = t_name

st.divider()

# --- 6. ORDERING & SETTLEMENT ---
col_menu, col_bill = st.columns()

with col_menu:
    st.subheader(f"🛒 Order: {st.session_state.current_table}")
    tabs = st.tabs(list(menu_df['Category'].unique()))
    for i, cat in enumerate(menu_df['Category'].unique()):
        with tabs[i]:
            items = menu_df[menu_df['Category'] == cat]
            m_cols = st.columns(3)
            for idx, row in items.iterrows():
                with m_cols[idx % 3]:
                    if st.button(f"{row['Item']}\n₹{row['Price']}", key=f"m_{idx}_{st.session_state.current_table}"):
                        st.session_state.active_orders[st.session_state.current_table].append({"Item": row['Item'], "Price": row['Price']})
                        st.rerun()

with col_bill:
    st.subheader("🧾 Bill Settle")
    order = st.session_state.active_orders[st.session_state.current_table]
    if order:
        total = sum([x['Price'] for x in order])
        for it in order: st.write(f"- {it['Item']} (₹{it['Price']})")
        st.write(f"### Total: ₹{total}")
        
        c_name = st.text_input("Customer Name")
        pay_mode = st.radio("Mode:", ["Cash", "Online", "Pending"], horizontal=True)
        
        if st.button("✅ Confirm & Send Bill", type="primary", use_container_width=True):
            # Save Sales
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_sale = pd.DataFrame([[now, st.session_state.current_table, total, pay_mode, "Done", c_name]], columns=['Date', 'Table', 'Total', 'Method', 'Status', 'Customer'])
            new_sale.to_csv(DB_FILE, mode='a', header=False, index=False)
            
            # WhatsApp Link
            wa_msg = f"Thanks for visiting *{CAFE_NAME}*! 📈\nTotal: ₹{total}\nFollow us: instagram.com/{info_df.iloc['Insta']}"
            wa_url = f"https://wa.me/91{c_name}?text={urllib.parse.quote(wa_msg)}"
            st.markdown(f'<a href="{wa_url}" target="_blank" class="insta-btn" style="background:#25D366;">📲 WhatsApp Bill</a>', unsafe_allow_html=True)
            
            st.session_state.active_orders[st.session_state.current_table] = []
            st.success("Table Cleared!")
    else:
        st.info("Table is empty.")
