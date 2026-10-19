import streamlit as st
import pandas as pd
from io import BytesIO
import time
import os
from dotenv import load_dotenv

# -------------------------------
# 1️⃣ Page Setup
# -------------------------------
st.set_page_config(
    page_title="EGSA Lottery Winners",
    layout="wide"
)

# -------------------------------
# 🖼️ Center Logo
# -------------------------------
logo_url = "https://raw.githubusercontent.com/Walfaanaa/AO/main/log.jpg"

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.image(logo_url, width=580)

# -------------------------------
# 🎨 Custom UI Style
# -------------------------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(to right,#4facfe,#00f2fe);
}

h1 {
    text-align:center;
}

.stButton>button {
    background-color:#ff4b4b;
    color:white;
    border-radius:12px;
    height:3em;
    width:200px;
    font-size:18px;
}

</style>
""", unsafe_allow_html=True)

st.title("EGSA Lottery Winners App (Authorized & One-Time Draw)")

st.markdown(
    """
    <h3 style='text-align:center;'>
    Welcome to the <b>EGSA Lottery Winners App</b>
    </h3>

    <p style='text-align:center; font-size:18px; color:green;'>
    This system ensures fair, transparent, and one-time-only draws managed by authorized personnel.
    </p>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# 2️⃣ Load Members Data
# -------------------------------
DATA_FILE = "AO_uqubii.xlsx"
WINNER_FILE = "winners_record.xlsx"

try:
    members_df = pd.read_excel(DATA_FILE)

    # Remove unwanted Excel index columns
    members_df = members_df.loc[
        :,
        ~members_df.columns.astype(str).str.contains("^Unnamed")
    ]

    # Add numbering column starting from 1
    members_display = members_df.copy()
    members_display.insert(
        0,
        "No",
        range(1, len(members_display) + 1)
    )

    st.success(
        f"✅ {len(members_df)} members loaded successfully from {DATA_FILE}."
    )

    st.dataframe(
        members_display,
        hide_index=True,
        use_container_width=True
    )

except FileNotFoundError:
    st.error(
        f"❌ {DATA_FILE} file not found! Please upload it to your app folder."
    )
    st.stop()

# -------------------------------
# 3️⃣ Admin Authorization
# -------------------------------
def get_admin_password():
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        load_dotenv()
        return os.getenv("STREAMLIT_ADMIN_PASSWORD")

def get_reset_password():
    load_dotenv()
    return os.getenv("STREAMLIT_RESET_PASSWORD")

AUTHORIZED_CODE = get_admin_password()
RESET_PASSWORD = get_reset_password()

if AUTHORIZED_CODE is None:
    st.warning(
        "⚠️ Admin password not set! Add it to Streamlit Secrets or .env file."
    )

password = st.text_input(
    "🔐 Enter admin passcode to enable draw:",
    type="password"
)

# -------------------------------
# 4️⃣ If Authorized
# -------------------------------
if password == AUTHORIZED_CODE:

    st.success("✅ Access granted! You can now enable the draw.")

    if os.path.exists(WINNER_FILE):

        with st.expander("⚙️ Admin Reset Options"):

            st.warning(
                "⚠️ A previous draw has already been conducted."
            )

            reset_pass_input = st.text_input(
                "Enter reset password to reset draw",
                type="password"
            )

            if st.button("🔄 Reset for New Round (Admin Only)"):

                if reset_pass_input == RESET_PASSWORD:
                    os.remove(WINNER_FILE)
                    st.success(
                        "✅ Winners record deleted. You can now run a new draw."
                    )
                    st.rerun()
                else:
                    st.error("❌ Incorrect reset password.")

        # -------------------------------
        # Show Previous Winners
        # -------------------------------
        previous_winners = pd.read_excel(WINNER_FILE)

        previous_winners = previous_winners.loc[
            :,
            ~previous_winners.columns.astype(str).str.contains("^Unnamed")
        ]

        if "No" not in previous_winners.columns:
            previous_winners.insert(
                0,
                "No",
                range(1, len(previous_winners) + 1)
            )

        st.subheader("🎉 Previous Winners")

        st.dataframe(
            previous_winners,
            hide_index=True,
            use_container_width=True
        )

    else:

        # -------------------------------
        # 5️⃣ Pick Winners
        # -------------------------------
        num_winners = st.number_input(
            "🏆 Number of winners to select",
            min_value=1,
            max_value=len(members_df),
            value=1
        )

        if st.button("🎲 Pick Winners"):

            with st.spinner(
                "🎲 Drawing lottery winners... Please wait"
            ):

                progress_text = st.empty()
                progress_bar = st.progress(0)

                for i in range(101):
                    time.sleep(0.02)
                    progress_text.text(f"Progress: {i}%")
                    progress_bar.progress(i)

            winners = members_df.sample(
                n=num_winners
            ).reset_index(drop=True)

            winners.insert(
                0,
                "No",
                range(1, len(winners) + 1)
            )

            st.success("🎉 Winners Selected!")
            st.balloons()

            st.subheader("🏆 Winners List")

            st.dataframe(
                winners,
                hide_index=True,
                use_container_width=True
            )

            # Save winners
            winners.to_excel(
                WINNER_FILE,
                index=False
            )

            # -------------------------------
            # Download Excel
            # -------------------------------
            def convert_df_to_excel(df):
                output = BytesIO()

                with pd.ExcelWriter(
                    output,
                    engine="xlsxwriter"
                ) as writer:
                    df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Winners"
                    )

                return output.getvalue()

            excel_data = convert_df_to_excel(winners)

            st.download_button(
                label="💾 Download Winners as Excel",
                data=excel_data,
                file_name="EGSA_lottery_winners.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# -------------------------------
# 6️⃣ If Wrong Password
# -------------------------------
elif password:
    st.error("❌ Invalid passcode. Access denied.")
    st.info(
        "You can view the member list, but only authorized staff can pick winners."
    )
