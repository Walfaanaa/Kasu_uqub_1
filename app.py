import streamlit as st
import pandas as pd
import time
from datetime import datetime

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Odaa Namee Hotel System", layout="wide")

# -----------------------------
# 🎨 GLOBAL STYLE (BACKGROUND + HEADER)
# -----------------------------
st.markdown(
    """
    <style>

    /* 🔴🟢 RED-GREEN-RED BACKGROUND */
    .stApp {
        background: linear-gradient(90deg, red, green, red);
        background-attachment: fixed;
        color: white;
    }

    /* 🔵 TOP HEADER (SHARE BAR AREA) */
    header[data-testid="stHeader"] {
        background-color: #1e3a8a !important;
    }

    header[data-testid="stHeader"] * {
        color: white !important;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.4);
    }

    /* DATAFRAMES CARD STYLE */
    div[data-testid="stDataFrame"] {
        background-color: rgba(255,255,255,0.90);
        border-radius: 10px;
        padding: 10px;
    }

    /* INPUT FIELDS */
    input, select, textarea {
        border-radius: 8px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 🌈 ANIMATED WELCOME TITLE
# -----------------------------
colors = ["#ff0000", "#00cc44", "#ff0000"]

if "color_index" not in st.session_state:
    st.session_state.color_index = 0

if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

if time.time() - st.session_state.last_update > 10:
    st.session_state.color_index = (st.session_state.color_index + 1) % len(colors)
    st.session_state.last_update = time.time()
    st.rerun()

current_color = colors[st.session_state.color_index]

st.markdown(
    f"""
    <h1 style='text-align:center; color:{current_color}; font-size:52px;'>
        🏨 Welcome to Odaa Namee Hotel
    </h1>
    <h3 style='text-align:center; color:white;'>
        Luxury • Comfort • Excellence
    </h3>
    <hr style='border:1px solid white;'>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 📦 SESSION STATE INIT
# -----------------------------
if "menu" not in st.session_state:
    st.session_state.menu = [
        {"name": "Pasta", "price": 120},
        {"name": "Burger", "price": 100},
        {"name": "Coffee", "price": 30},
        {"name": "Injera Special", "price": 90}
    ]

if "rooms" not in st.session_state:
    st.session_state.rooms = [
        {"room_no": 101, "type": "Standard", "status": "Available"},
        {"room_no": 102, "type": "Deluxe", "status": "Available"},
        {"room_no": 201, "type": "Suite", "status": "Occupied"}
    ]

if "orders" not in st.session_state:
    st.session_state.orders = []

if "guests" not in st.session_state:
    st.session_state.guests = []

# -----------------------------
# 📌 SIDEBAR MENU
# -----------------------------
st.sidebar.title("🏨 Odaa Namee Hotel")

menu_option = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Menu", "Rooms", "Room Service", "Guests", "Billing"]
)

# -----------------------------
# 📊 DASHBOARD
# -----------------------------
if menu_option == "Dashboard":
    st.title("📊 Hotel Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rooms", len(st.session_state.rooms))
    col2.metric("Guests", len(st.session_state.guests))
    col3.metric("Orders", len(st.session_state.orders))

    st.subheader("🛏 Room Status")
    st.dataframe(pd.DataFrame(st.session_state.rooms))

# -----------------------------
# 🍽 MENU
# -----------------------------
elif menu_option == "Menu":
    st.title("🍽 Menu Management")

    name = st.text_input("Meal Name")
    price = st.number_input("Price", min_value=0)

    if st.button("Add Meal"):
        if name:
            st.session_state.menu.append({"name": name, "price": price})
            st.success("Meal added successfully!")

    st.subheader("Current Menu")
    st.dataframe(pd.DataFrame(st.session_state.menu))

# -----------------------------
# 🛏 ROOMS
# -----------------------------
elif menu_option == "Rooms":
    st.title("🛏 Room Management")

    room_no = st.number_input("Room Number", step=1)
    room_type = st.selectbox("Room Type", ["Standard", "Deluxe", "Suite", "Family"])

    if st.button("Add Room"):
        st.session_state.rooms.append({
            "room_no": room_no,
            "type": room_type,
            "status": "Available"
        })
        st.success("Room added successfully!")

    st.subheader("Room List")
    st.dataframe(pd.DataFrame(st.session_state.rooms))

# -----------------------------
# 🛎 ROOM SERVICE
# -----------------------------
elif menu_option == "Room Service":
    st.title("🛎 Room Service Orders")

    guest_name = st.text_input("Guest Name")
    item = st.selectbox("Select Item", [m["name"] for m in st.session_state.menu])
    qty = st.number_input("Quantity", min_value=1, value=1)

    if st.button("Place Order"):
        price = next(m["price"] for m in st.session_state.menu if m["name"] == item)

        st.session_state.orders.append({
            "guest": guest_name,
            "item": item,
            "qty": qty,
            "total": price * qty,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        st.success("Order placed successfully!")

    st.subheader("Orders List")
    st.dataframe(pd.DataFrame(st.session_state.orders))

# -----------------------------
# 👤 GUESTS
# -----------------------------
elif menu_option == "Guests":
    st.title("👤 Guest Management")

    name = st.text_input("Guest Name")
    phone = st.text_input("Phone Number")
    room = st.number_input("Room Number", step=1)

    if st.button("Register Guest"):
        st.session_state.guests.append({
            "name": name,
            "phone": phone,
            "room": room,
            "check_in": datetime.now().strftime("%Y-%m-%d")
        })
        st.success("Guest registered successfully!")

    st.subheader("Guest List")
    st.dataframe(pd.DataFrame(st.session_state.guests))

# -----------------------------
# 💰 BILLING
# -----------------------------
elif menu_option == "Billing":
    st.title("💰 Billing System")

    if st.session_state.orders:
        df = pd.DataFrame(st.session_state.orders)

        st.metric("Total Revenue (ETB)", df["total"].sum())

        st.subheader("Order Details")
        st.dataframe(df)
    else:
        st.info("No orders yet.")
