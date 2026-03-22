import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
import os

# --- CONFIG ---
CAFE_NAME = "The Trader's Cafe"
# AAPKE LINKS
INSTA_URL = "https://www.instagram.com/the_trader_cafe?igsh=bHVzcm1pbWY4MXlq"
GOOGLE_REVIEW_URL = "https://g.page/r/YOUR_GOOGLE_REVIEW_LINK/review" # <-- Yahan apna Google Review link dalein

st.set_page_config(page_title=CAFE_NAME, layout="wide")

# --- TRADING THEME CSS ---
st.markdown(f"""
    <style>
    .main {{ background-color: #0e1117; color: white; }}
    .social-card {{
        background: #1e2130;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #00ff41;
        text-align: center;
        margin-top: 10px;
    }}
    .review-btn {{
        background-color: #4285F4; /* Google Blue */
        color: white !important;
        padding: 12px;
        text-decoration: none;
        border-radius: 10px;
        display: block;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    .insta-btn {{
        background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); 
        color: white !important;
        padding: 12px;
        text-decoration: none;
        border-radius: 10px;
        display: block;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'active_orders' not in st.session_state:
    st.session_state.active_orders = {f"Table {i}": [] for i in range(1, 21)}

# --- HEADER ---
st.title(f"📈 {CAFE_NAME}")
st.caption("Bake Your Taste | Profit in Every Bite")
st.divider()

# --- TABLE GRID (1 to 20) ---
cols = st.columns(10)
for i in range(1, 21):
    t_name = f"Table {i}"
    with cols[(i-1)%10]:
        is_occ = len(st.session_state.active_orders[t_name]) > 0
        if st.button(f"{i}\n{'🔴' if is_occ else '🟢'}", key=f"t_{i}", use_container_width=True):
            st.session_state.current_table = t_name

# --- BILLING & SOCIAL CONNECT ---
if 'current_table' in st.session_state:
    st.write(f"### 📑 Active Terminal: {st.session_state.current_table}")
    order = st.session_state.active_orders[st.session_state.current_table]
    
    col_menu, col_actions = st.columns()
    
    with col_menu:
        # Aapka Menu yahan aayega (Combos etc.)
        if st.button("📈 Add Forex Combo (₹299)"):
            st.session_state.active_orders[st.session_state.current_table].append({"Item": "Forex Combo", "Price": 299})
            st.rerun()

    with col_actions:
        if order:
            total = sum([x['Price'] for x in order])
            st.subheader(f"Total: ₹{total}")
            phone = st.text_input("Customer Phone", "91")
            
            if st.button("✅ Settle & Get Review", type="primary", use_container_width=True):
                # 1. WhatsApp Message including both links
                wa_msg = (f"Thanks for visiting *{CAFE_NAME}*! 📈\n"
                          f"Bill: *₹{total}*\n\n"
                          f"🌟 Rate us on Google: {GOOGLE_REVIEW_URL}\n"
                          f"📸 Follow us on Insta: {INSTA_URL}")
                wa_link = f"https://wa.me/{phone}?text={urllib.parse.quote(wa_msg)}"
                
                # 2. Show Social Card for Customer
                st.markdown(f"""
                    <div class="social-card">
                        <h4>Help us Grow, Prasad! 🚀</h4>
                        <a href="{GOOGLE_REVIEW_URL}" target="_blank" class="review-btn">⭐ Rate us 5-Star on Google</a>
                        <a href="{INSTA_URL}" target="_blank" class="insta-btn">📸 Follow on Instagram</a>
                        <br>
                        <a href="{wa_link}" target="_blank" style="color:#25D366; font-weight:bold;">📲 Send WhatsApp Bill</a>
                    </div>
                """, unsafe_allow_html=True)
                
                # 3. Clear Table
                st.session_state.active_orders[st.session_state.current_table] = []
        else:
            st.info("Table is empty.")
