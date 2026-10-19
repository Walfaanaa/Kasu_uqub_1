import streamlit as st
import sqlite3
import hashlib

# -----------------------------
# Database Setup
# -----------------------------
conn = sqlite3.connect("lottery.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    phone TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS lottery (
    phone TEXT UNIQUE,
    chosen_number INTEGER UNIQUE
)
""")
conn.commit()


# -----------------------------
# Password Hash Function
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -----------------------------
# Register / Login
# -----------------------------
st.title("🎯 Lottery App (1-100)")

menu = st.sidebar.selectbox("Menu", ["Register", "Login"])

if menu == "Register":
    st.subheader("Create Account")
    phone = st.text_input("Phone Number (Customer ID)")
    password = st.text_input("Create Password", type="password")

    if st.button("Register"):
        if phone and password:
            try:
                cursor.execute(
                    "INSERT INTO users (phone, password) VALUES (?, ?)",
                    (phone, hash_password(password))
                )
                conn.commit()
                st.success("Account created successfully!")
            except:
                st.error("Phone number already registered.")
        else:
            st.warning("Please fill all fields.")


if menu == "Login":
    st.subheader("Login")
    phone = st.text_input("Phone Number")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cursor.execute(
            "SELECT * FROM users WHERE phone=? AND password=?",
            (phone, hash_password(password))
        )
        user = cursor.fetchone()

        if user:
            st.success("Login Successful!")

            # Show available numbers
            cursor.execute("SELECT chosen_number FROM lottery")
            taken_numbers = [row[0] for row in cursor.fetchall()]

            available_numbers = [n for n in range(1, 101) if n not in taken_numbers]

            if phone in [row[0] for row in cursor.execute("SELECT phone FROM lottery").fetchall()]:
                st.info("You already selected your number.")
            else:
                choice = st.selectbox("Choose your lottery number", available_numbers)

                if st.button("Confirm Number"):
                    try:
                        cursor.execute(
                            "INSERT INTO lottery (phone, chosen_number) VALUES (?, ?)",
                            (phone, choice)
                        )
                        conn.commit()
                        st.success(f"Number {choice} successfully registered!")
                    except:
                        st.error("Number already taken.")

        else:
            st.error("Invalid phone number or password.")