import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- CONFIG ---
CAFE_NAME = "The Trader's Cafe"
# AAPKA EXACT INSTAGRAM LINK
INSTA_URL = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"
DB_FILE = 'cafe_sales.csv'

st.set_page_config(page_title=CAFE_NAME, layout="wide")

# --- CUSTOM TRADING THEME CSS ---
st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; color: white; }}
    .insta-btn {{
        background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); 
        color: white !important;
        padding: 12px;
        text-decoration: none;
        border-radius: 10px;
        display: block;
        text-align: center;
        font-weight: bold;
        margin-top: 10px;
    }}
    .wa-btn {{
        background-color: #25D366;
        color: white !important;
        padding: 12px;
        text-decoration: none;
        border-radius: 10px;
        display: block;
        text-align: center;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'active_orders' not in st.session_state:
    st.session_state.active_orders = {f"Table {i}": [] for i in range(1, 21)}
if 'current_table' not in st.session_state:
    st.session_state.current_table = "Table 1"

# --- HEADER ---
st.title(f"📈 {CAFE_NAME}")
st.write(f"[📸 Visit Our Instagram]({INSTA_URL})")
st.divider()

# --- TABLE GRID ---
cols = st.columns(10)
for i in range(1, 21):
    t_name = f"Table {i}"
    with cols[(i-1)%10]:
        is_occ = len(st.session_state.active_orders[t_name]) > 0
        if st.button(f"{i}\n{'🔴' if is_occ else '🟢'}", key=f"t_{i}", use_container_width=True):
            st.session_state.current_table = t_name

# --- BILLING & SETTLEMENT ---
col_menu, col_bill = st.columns()

with col_menu:
    st.subheader(f"🛒 Menu for {st.session_state.current_table}")
    # Example: Forex Combo Add button
    if st.button("📈 Add Forex Combo (₹299)"):
        st.session_state.active_orders[st.session_state.current_table].append({"Item": "Forex Combo", "Price": 299})
        st.rerun()

with col_bill:
    st.subheader("💳 Settlement")
    order = st.session_state.active_orders[st.session_state.current_table]
    if order:
        total = sum([x['Price'] for x in order])
        st.write(f"**Total Amount: ₹{total}**")
        phone = st.text_input("Customer Phone", "91")
        
        if st.button("✅ Settle Bill", type="primary", use_container_width=True):
            # 1. WhatsApp Message with Insta Link
            wa_msg = (f"Thanks for visiting *{CAFE_NAME}*! ☕\n"
                      f"Total Bill: *₹{total}*\n\n"
                      f"Tag us on Instagram & get offers: \n{INSTA_URL}\n\n"
                      f"Bake Your Taste! 🥧")
            
            wa_link = f"https://wa.me/{phone}?text={urllib.parse.quote(wa_msg)}"
            
            # 2. Display Action Buttons
            st.success("Bill Settled!")
            st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">📲 Send WhatsApp Bill</a>', unsafe_allow_html=True)
            st.markdown(f'<a href="{INSTA_URL}" target="_blank" class="insta-btn">📸 Open Instagram Profile</a>', unsafe_allow_html=True)
            
            # 3. Clear Table
            st.session_state.active_orders[st.session_state.current_table] = []
    else:
        st.info("Table is empty.")
