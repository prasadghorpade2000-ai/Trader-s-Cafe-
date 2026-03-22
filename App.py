import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- 1. SETTINGS & THEME ---
CAFE_NAME = "The Trader's Cafe"
TAGLINE = "Bake Your Taste | Profit in Every Bite 📈"
ADMIN_PASSWORD = "Prasad@123"
MENU_FILE = 'menu_data.csv'
DB_FILE = 'cafe_sales.csv'

st.set_page_config(page_title=CAFE_NAME, layout="wide")

# Custom Dark Trading Theme
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { border-radius: 10px; font-weight: bold; height: 50px; width: 100%; border: 1px solid #333; }
    div[data-testid="stMetricValue"] { color: #00ff41; }
    .wa-btn { background-color: #25D366; color: white !important; padding: 12px; text-decoration: none; border-radius: 10px; display: block; text-align: center; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA INITIALIZATION ---
if not os.path.isfile(MENU_FILE):
    initial_menu = [
        ['🎂 Cakes', 'Chocolate Dutch', 350],
        ['🎂 Cakes', 'Red Velvet', 450],
        ['🍕 Pizza', 'Forex Special Paneer', 199],
        ['🍔 Burger', 'Nifty Classic', 89],
        ['🔥 Offer', 'Burger + Drink + Brownie', 59]
    ]
    pd.DataFrame(initial_menu, columns=['Category', 'Item', 'Price']).to_csv(MENU_FILE, index=False)

if not os.path.isfile(DB_FILE):
    pd.DataFrame(columns=['Date', 'Table', 'Total', 'Method', 'Status', 'Customer']).to_csv(DB_FILE, index=False)

menu_df = pd.read_csv(MENU_FILE)

# --- 3. SESSION STATE ---
if 'active_orders' not in st.session_state:
    st.session_state.active_orders = {f"Table {i}": [] for i in range(1, 21)}
if 'current_table' not in st.session_state:
    st.session_state.current_table = "Table 1"

# --- 4. ADMIN PANEL ---
st.sidebar.title("🔐 Admin Control")
pwd = st.sidebar.text_input("Password", type="password")

if pwd == ADMIN_PASSWORD:
    admin_tab = st.sidebar.radio("Go to:", ["Sales Summary", "Edit Menu/Rates"])
    
    if admin_tab == "Edit Menu/Rates":
        st.write("### 🛠️ Menu Editor")
        new_menu = st.data_editor(menu_df, num_rows="dynamic")
        if st.button("Save Changes"):
            new_menu.to_csv(MENU_FILE, index=False)
            st.success("Menu Updated!")
            st.rerun()
            
    if admin_tab == "Sales Summary":
        df_sales = pd.read_csv(DB_FILE)
        st.write("### 📊 Sales Report")
        st.metric("Total Business", f"₹{df_sales['Total'].sum()}")
        st.dataframe(df_sales.tail(20))

# --- 5. MAIN UI: TABLE TRACKER ---
st.title(f"📈 {CAFE_NAME}")
st.caption(TAGLINE)

st.write("### 🪑 Select Table")
t_cols = st.columns(10) # Isme 10 columns fix hain
for i in range(1, 21):
    t_name = f"Table {i}"
    with t_cols[(i-1)%10]:
        is_occ = len(st.session_state.active_orders[t_name]) > 0
        btn_label = f"{i}\n{'🔴' if is_occ else '🟢'}"
        if st.button(btn_label, key=f"t_btn_{i}"):
            st.session_state.current_table = t_name

st.divider()

# --- 6. ORDERING & SETTLEMENT ---
col_menu, col_bill = st.columns() # Yahan fix kar diya hai daalkar

with col_menu:
    st.subheader(f"🛒 Menu: {st.session_state.current_table}")
    cats = menu_df['Category'].unique()
    tabs = st.tabs(list(cats))
    for i, cat in enumerate(cats):
        with tabs[i]:
            items = menu_df[menu_df['Category'] == cat]
            item_cols = st.columns(2)
            for idx, row in items.iterrows():
                with item_cols[idx % 2]:
                    if st.button(f"{row['Item']} (₹{row['Price']})", key=f"add_{idx}_{st.session_state.current_table}"):
                        st.session_state.active_orders[st.session_state.current_table].append(
                            {"Item": row['Item'], "Price": row['Price']}
                        )
                        st.rerun()

with col_bill:
    st.subheader("🧾 Active Bill")
    current_order = st.session_state.active_orders[st.session_state.current_table]
    
    if current_order:
        total = sum([x['Price'] for x in current_order])
        for item in current_order:
            st.write(f"- {item['Item']}: ₹{item['Price']}")
        st.write(f"## Total: ₹{total}")
        
        phone = st.text_input("Customer Phone (91...)", value="91")
        pay_mode = st.selectbox("Payment Mode", ["Cash", "Online", "Pending"])
        
        if st.button("Settle & Clear Table ✅", type="primary", use_container_width=True):
            # Save to Database
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_entry = pd.DataFrame([[now, st.session_state.current_table, total, pay_mode, "Done", phone]], 
                                     columns=['Date', 'Table', 'Total', 'Method', 'Status', 'Customer'])
            new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
            
            # WhatsApp Msg
            msg = f"Thanks for visiting *{CAFE_NAME}*! 📈\nYour Bill: *₹{total}*\nBake Your Taste! 🥧"
            wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn">📲 Send WhatsApp Bill</a>', unsafe_allow_html=True)
            
            # Clear Table
            st.session_state.active_orders[st.session_state.current_table] = []
            st.success("Table Settled!")
    else:
        st.info("No items added yet.")
