import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- 1. CONFIG & THEME ---
CAFE_NAME = "The Trader's Cafe"
TAGLINE = "Bake Your Taste | Profit in Every Bite 📈"
ADMIN_PASSWORD = "Prasad@123"
MENU_FILE = 'menu_data.csv'
DB_FILE = 'cafe_sales.csv'
# AAPKA INSTAGRAM LINK
INSTA_LINK = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"

st.set_page_config(page_title=CAFE_NAME, layout="wide")

# Custom Dark Trading Theme
st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; color: white; }}
    .stButton>button {{ border-radius: 10px; font-weight: bold; height: 50px; width: 100%; border: 1px solid #333; background-color: #1e2130; color: white; }}
    div[data-testid="stMetricValue"] {{ color: #00ff41; }}
    .wa-btn {{ background-color: #25D366; color: white !important; padding: 15px; text-decoration: none; border-radius: 10px; display: block; text-align: center; font-weight: bold; margin-bottom: 10px; }}
    .insta-btn {{ background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #bc1888); color: white !important; padding: 15px; text-decoration: none; border-radius: 10px; display: block; text-align: center; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. MENU DATABASE (SAARE ITEMS YAHAN HAIN) ---
if not os.path.isfile(MENU_FILE):
    initial_menu = [
        ['🎂 Cakes', 'Chocolate Dutch (1/2 kg)', 350],
        ['🎂 Cakes', 'Red Velvet (1/2 kg)', 450],
        ['🎂 Cakes', 'Black Forest', 300],
        ['🍕 Pizza', 'Forex Special Paneer', 199],
        ['🍕 Pizza', 'Margherita Classic', 149],
        ['🍕 Pizza', 'Trader Veggie Feast', 179],
        ['🍔 Burger', 'Nifty Aloo Tikki', 79],
        ['🍔 Burger', 'Bullish Cheese Burger', 119],
        ['🥪 Sandwich', 'Veg Grilled Sandwich', 89],
        ['🥪 Sandwich', 'Paneer Club Sandwich', 129],
        ['🥤 Drinks', 'Cold Coffee', 60],
        ['🥤 Drinks', 'Hot Tea/Coffee', 20],
        ['🔥 Offer', 'Burger + Fries + Coke', 159]
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
st.sidebar.title("🔐 Admin Panel")
pwd = st.sidebar.text_input("Password", type="password")

if pwd == ADMIN_PASSWORD:
    admin_tab = st.sidebar.radio("Navigation:", ["Today's Sales", "Edit Menu/Rates"])
    
    if admin_tab == "Edit Menu/Rates":
        st.write("### 🛠️ Menu & Rate Editor")
        new_menu = st.data_editor(menu_df, num_rows="dynamic", key="menu_editor")
        if st.button("Update Menu Permanently"):
            new_menu.to_csv(MENU_FILE, index=False)
            st.success("Rates Updated!")
            st.rerun()
            
    if admin_tab == "Today's Sales":
        df_sales = pd.read_csv(DB_FILE)
        st.write("### 📊 Business Summary")
        if not df_sales.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Net Sale", f"₹{df_sales['Total'].sum()}")
            c2.metric("Cash In", f"₹{df_sales[df_sales['Method']=='Cash']['Total'].sum()}")
            c3.metric("Online In", f"₹{df_sales[df_sales['Method']=='Online']['Total'].sum()}")
            st.dataframe(df_sales.tail(20))

# --- 5. MAIN INTERFACE ---
st.title(f"📈 {CAFE_NAME}")
st.write(f"**{TAGLINE}**")

# --- TABLE GRID (1 to 20) ---
st.write("### 🪑 Table Selection")
t_cols = st.columns(10)
for i in range(1, 21):
    t_name = f"Table {i}"
    with t_cols[(i-1)%10]:
        is_occ = len(st.session_state.active_orders[t_name]) > 0
        btn_txt = f"{i}\n{'🔴' if is_occ else '🟢'}"
        if st.button(btn_txt, key=f"t_btn_{i}"):
            st.session_state.current_table = t_name

st.divider()

# --- 6. ORDERING & SETTLEMENT ---
col_menu, col_bill = st.columns()

with col_menu:
    st.subheader(f"🛒 Menu: {st.session_state.current_table}")
    cats = menu_df['Category'].unique()
    tabs = st.tabs(list(cats))
    for i, cat in enumerate(cats):
        with tabs[i]:
            items = menu_df[menu_df['Category'] == cat]
            # Use 2 columns for items inside tabs
            item_cols = st.columns(2)
            for idx, row in items.iterrows():
                with item_cols[idx % 2]:
                    if st.button(f"{row['Item']} (₹{row['Price']})", key=f"it_{idx}"):
                        st.session_state.active_orders[st.session_state.current_table].append(
                            {"Item": row['Item'], "Price": row['Price']}
                        )
                        st.rerun()

with col_bill:
    st.subheader("🧾 Active Bill")
    curr_order = st.session_state.active_orders[st.session_state.current_table]
    
    if curr_order:
        total = sum([x['Price'] for x in curr_order])
        for it in curr_order:
            st.write(f"• {it['Item']} - ₹{it['Price']}")
        st.write(f"## Total: ₹{total}")
        
        phone = st.text_input("Customer Phone", value="91")
        pay_mode = st.selectbox("Payment Mode", ["Cash", "Online", "Pending"])
        
        if st.button("Settle & Send Bill ✅", type="primary"):
            # Save Sales
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            new_entry = pd.DataFrame([[now, st.session_state.current_table, total, pay_mode, "Done", phone]], 
                                     columns=['Date', 'Table', 'Total', 'Method', 'Status', 'Customer'])
            new_entry.to_csv(DB_FILE, mode='a', header=False, index=False)
            
            # WhatsApp Message Logic
            wa_msg = f"Thanks for visiting *{CAFE_NAME}*! 📈\nBill: *₹{total}*\nTag us: {INSTA_LINK}"
            wa_url = f"https://wa.me/{phone}?text={urllib.parse.quote(wa_msg)}"
            
            st.success("Bill Settled!")
            # Display Big Buttons for WA and Instagram
            st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn">📲 WhatsApp Bill</a>', unsafe_allow_html=True)
            st.markdown(f'<a href="{INSTA_LINK}" target="_blank" class="insta-btn">📸 Follow us on Instagram</a>', unsafe_allow_html=True)
            
            # Clear Table
            st.session_state.active_orders[st.session_state.current_table] = []
    else:
        st.info("Table is empty. Add items from the menu.")
