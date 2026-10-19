
import os
import time
import hmac
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ==================================================
# 1. PAGE SETUP
# ==================================================
st.set_page_config(
    page_title="EGSA Lottery Winners",
    page_icon="🎉",
    layout="wide"
)

APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "Kaasuu.xlsx"
WINNER_FILE = APP_DIR / "winners_record.xlsx"
ENV_FILE = APP_DIR / ".env"

# Load .env from the application directory.
# Streamlit Secrets take priority over environment variables.
load_dotenv(dotenv_path=ENV_FILE, override=False)


def get_setting(secret_key, env_key):
    """Read a setting from Streamlit Secrets, then environment variables."""
    try:
        value = st.secrets.get(secret_key)
        if value is not None and str(value).strip():
            return str(value)
    except Exception:
        pass

    value = os.getenv(env_key)
    return value if value and value.strip() else None


AUTHORIZED_CODE = get_setting(
    "ADMIN_PASSWORD",
    "STREAMLIT_ADMIN_PASSWORD"
)

RESET_PASSWORD = get_setting(
    "RESET_PASSWORD",
    "STREAMLIT_RESET_PASSWORD"
)

# ==================================================
# 2. CUSTOM UI
# ==================================================
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #4facfe, #00f2fe);
    }

    h1 {
        text-align: center;
    }

    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 12px;
        min-height: 3em;
        font-size: 18px;
        border: none;
    }

    .stButton > button:hover {
        background-color: #d93636;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==================================================
# 3. CENTER LOGO AND TITLE
# ==================================================
logo_url = "https://raw.githubusercontent.com/Walfaanaa/AO/main/log.jpg"

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.image(logo_url, width=580)

st.title("EGSA Lottery Winners App")

st.markdown(
    """
    <h3 style="text-align:center;">
        Welcome to the <b>EGSA Lottery Winners App</b>
    </h3>

    <p style="text-align:center; font-size:18px; color:green;">
        A transparent, fair, and one-time lottery draw managed
        by authorized personnel.
    </p>
    """,
    unsafe_allow_html=True
)

st.divider()

# ==================================================
# 4. LOAD MEMBERS
# ==================================================
if not DATA_FILE.exists():
    st.error(
        f"❌ Member file not found: {DATA_FILE.name}. "
        "Place Kaasuu.xlsx in the application folder."
    )
    st.stop()

try:
    members_df = pd.read_excel(DATA_FILE)

    # Remove unwanted Excel index columns.
    members_df = members_df.loc[
        :,
        ~members_df.columns.astype(str).str.contains(
            r"^Unnamed", case=False, regex=True
        )
    ]

    if members_df.empty:
        st.error("The member file contains no members.")
        st.stop()

    if len(members_df.columns) == 0:
        st.error("The member file has no valid columns.")
        st.stop()

    members_display = members_df.copy()
    members_display.insert(
        0, "No", range(1, len(members_display) + 1)
    )

    st.success(
        f"✅ {len(members_df):,} members loaded successfully."
    )

    with st.expander("👥 View Member List", expanded=True):
        st.dataframe(
            members_display,
            hide_index=True,
            use_container_width=True
        )

except Exception as exc:
    st.error(f"Unable to read the member file: {exc}")
    st.stop()

# ==================================================
# 5. ADMIN AUTHORIZATION
# ==================================================
st.subheader("🔐 Administrator Access")

if not AUTHORIZED_CODE:
    st.error(
        "Admin password is not configured. "
        "Configure ADMIN_PASSWORD in Streamlit Secrets "
        "or STREAMLIT_ADMIN_PASSWORD in .env."
    )
    st.stop()

password = st.text_input(
    "Enter admin passcode to enable lottery operations:",
    type="password",
    key="admin_password_input"
)

is_authorized = bool(password) and hmac.compare_digest(
    password, AUTHORIZED_CODE
)

if password and not is_authorized:
    st.error("❌ Invalid passcode. Access denied.")
    st.info(
        "You can view the member list, but only authorized "
        "administrators can conduct or reset a draw."
    )

if not is_authorized:
    st.stop()

st.success("✅ Access granted. Administrator authenticated.")

# ==================================================
# 6. EXISTING DRAW: SHOW WINNERS OR OFFER RESET
# ==================================================
if WINNER_FILE.exists():

    st.warning(
        "⚠️ A draw record already exists. "
        "Another draw is disabled until an authorized reset."
    )

    try:
        previous_winners = pd.read_excel(WINNER_FILE)

        previous_winners = previous_winners.loc[
            :,
            ~previous_winners.columns.astype(str).str.contains(
                r"^Unnamed", case=False, regex=True
            )
        ]

        if "No" not in previous_winners.columns:
            previous_winners.insert(
                0, "No", range(1, len(previous_winners) + 1)
            )

        st.subheader("🏆 Previous Lottery Winners")

        st.dataframe(
            previous_winners,
            hide_index=True,
            use_container_width=True
        )

        output = BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            previous_winners.to_excel(
                writer, index=False, sheet_name="Winners"
            )

        st.download_button(
            label="💾 Download Previous Winners",
            data=output.getvalue(),
            file_name="EGSA_lottery_winners.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    except Exception as exc:
        st.error(f"Unable to read the winners record: {exc}")

    st.divider()
    st.subheader("⚙️ Administrator Reset")

    st.warning(
        "Resetting deletes the existing winners record and permits "
        "a new draw. Only proceed when a new round is authorized."
    )

    if not RESET_PASSWORD:
        st.error(
            "Reset password is not configured. "
            "Set RESET_PASSWORD in Streamlit Secrets or "
            "STREAMLIT_RESET_PASSWORD in .env."
        )
    else:
        reset_input = st.text_input(
            "Enter reset password:",
            type="password",
            key="reset_password_input"
        )

        confirm_reset = st.checkbox(
            "I confirm that the existing lottery record may be deleted."
        )

        if st.button("🔄 Reset for New Round", key="reset_draw"):

            if not reset_input or not hmac.compare_digest(
                reset_input, RESET_PASSWORD
            ):
                st.error("❌ Incorrect reset password.")

            elif not confirm_reset:
                st.warning("Please confirm the reset before continuing.")

            else:
                try:
                    WINNER_FILE.unlink()
                    st.success(
                        "✅ Winners record removed. "
                        "You may now conduct a new draw."
                    )
                    st.rerun()

                except OSError as exc:
                    st.error(f"Unable to reset the draw: {exc}")

# ==================================================
# 7. NO EXISTING DRAW: PICK WINNERS
# ==================================================
else:

    st.subheader("🎲 Conduct Lottery Draw")

    num_winners = st.number_input(
        "🏆 Number of winners to select:",
        min_value=1,
        max_value=len(members_df),
        value=1,
        step=1
    )

    confirm_draw = st.checkbox(
        "I confirm that I am authorized to conduct this lottery draw."
    )

    if st.button("🎲 Pick Winners", key="pick_winners"):

        if not confirm_draw:
            st.warning("Please confirm authorization before drawing.")

        elif WINNER_FILE.exists():
            st.error(
                "A winners record already exists. "
                "Refresh the page before proceeding."
            )
            st.rerun()

        else:
            try:
                with st.spinner("🎲 Drawing lottery winners..."):

                    progress_text = st.empty()
                    progress_bar = st.progress(0)

                    for i in range(101):
                        time.sleep(0.02)
                        progress_text.text(f"Drawing progress: {i}%")
                        progress_bar.progress(i)

                    winners = members_df.sample(
                        n=int(num_winners),
                        replace=False
                    ).reset_index(drop=True)

                    winners.insert(
                        0, "No", range(1, len(winners) + 1)
                    )

                    # Prepare Excel in memory first.
                    output = BytesIO()

                    with pd.ExcelWriter(
                        output, engine="xlsxwriter"
                    ) as writer:
                        winners.to_excel(
                            writer, index=False, sheet_name="Winners"
                        )

                    # Refuse to overwrite an existing draw record.
                    # Exclusive file creation protects against ordinary
                    # simultaneous attempts on the same local filesystem.
                    with open(WINNER_FILE, "xb") as file:
                        file.write(output.getvalue())

                progress_text.empty()
                progress_bar.empty()

                st.success("🎉 Lottery winners selected and saved!")
                st.balloons()

                st.subheader("🏆 Winners List")

                st.dataframe(
                    winners,
                    hide_index=True,
                    use_container_width=True
                )

                st.download_button(
                    label="💾 Download Winners as Excel",
                    data=output.getvalue(),
                    file_name="EGSA_lottery_winners.xlsx",
                    mime=(
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    )
                )

            except FileExistsError:
                st.error(
                    "A draw record was created by another operation. "
                    "No existing winners record was overwritten."
                )
                st.rerun()

            except Exception as exc:
                st.error(f"Unable to complete the draw: {exc}")

# ==================================================
# 8. FOOTER
# ==================================================
st.divider()

st.caption(
    "EGSA2025 | Lottery Winners Management System"
)
