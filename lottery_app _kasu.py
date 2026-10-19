import os
import hmac
import time
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# 1. PAGE SETUP AND FILE PATHS
# ============================================================

st.set_page_config(
    page_title="EGSA Lottery Winners",
    page_icon="🎉",
    layout="wide"
)

APP_DIR = Path(__file__).resolve().parent

ENV_FILE = APP_DIR / ".env"
DATA_FILE = APP_DIR / "Kaasuu.xlsx"
WINNER_FILE = APP_DIR / "winners_record.xlsx"

# Load environment variables from the app's own folder.
load_dotenv(dotenv_path=ENV_FILE, override=True)


# ============================================================
# 2. LOAD ADMIN AND RESET PASSWORDS
# ============================================================

def get_setting(secret_key, env_key):
    """
    Read a setting from Streamlit Secrets first.
    If it is unavailable, read it from the .env file.
    Never display the actual password.
    """
    try:
        value = st.secrets[secret_key]
        if value is not None and str(value).strip():
            return str(value).strip(), "Streamlit Secrets"
    except Exception:
        pass

    value = os.getenv(env_key)

    if value is not None and value.strip():
        return value.strip(), ".env / environment"

    return None, None


AUTHORIZED_CODE, ADMIN_PASSWORD_SOURCE = get_setting(
    "ADMIN_PASSWORD",
    "STREAMLIT_ADMIN_PASSWORD"
)

RESET_PASSWORD, RESET_PASSWORD_SOURCE = get_setting(
    "RESET_PASSWORD",
    "STREAMLIT_RESET_PASSWORD"
)


def password_matches(entered_password, expected_password):
    """Compare passwords without displaying either value."""
    if not entered_password or not expected_password:
        return False

    return hmac.compare_digest(
        entered_password.strip(),
        expected_password
    )


# ============================================================
# 3. CENTER LOGO
# ============================================================

logo_url = "https://raw.githubusercontent.com/Walfaanaa/AO/main/log.jpg"

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    st.image(logo_url, width=580)


# ============================================================
# 4. CUSTOM UI STYLE
# ============================================================

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
        width: 100%;
        font-size: 18px;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.title("EGSA Lottery Winners App")

st.markdown(
    """
    <h3 style="text-align:center;">
        Welcome to the <b>EGSA Lottery Winners App</b>
    </h3>

    <p style="text-align:center; font-size:18px; color:green;">
        Fair, transparent, and authorized lottery draws.
    </p>
    """,
    unsafe_allow_html=True
)


# ============================================================
# 5. LOAD AND DISPLAY MEMBERS
# ============================================================

if not DATA_FILE.is_file():
    st.error(
        f"Member file not found: {DATA_FILE.name}. "
        "Please place the Excel file in the application folder."
    )
    st.stop()

try:
    members_df = pd.read_excel(DATA_FILE)

    # Remove unwanted Excel index columns.
    members_df = members_df.loc[
        :,
        ~members_df.columns.astype(str).str.contains(
            r"^Unnamed",
            case=False,
            regex=True
        )
    ].copy()

    if members_df.empty:
        st.error("The member Excel file contains no member records.")
        st.stop()

    # Remove fully empty rows.
    members_df = members_df.dropna(how="all").reset_index(drop=True)

    if members_df.empty:
        st.error("No valid member records were found.")
        st.stop()

    # Avoid a duplicate numbering column.
    if "No" in members_df.columns:
        members_df = members_df.drop(columns=["No"])

    members_display = members_df.copy()
    members_display.insert(
        0,
        "No",
        range(1, len(members_display) + 1)
    )

    st.success(
        f"{len(members_df):,} members loaded successfully."
    )

    with st.expander("View Member List", expanded=True):
        st.dataframe(
            members_display,
            hide_index=True,
            use_container_width=True
        )

except Exception as exc:
    st.error(
        "Unable to read the member Excel file. "
        "Please check its format and column headers."
    )
    st.exception(exc)
    st.stop()


# ============================================================
# 6. ADMIN AUTHORIZATION
# ============================================================

st.divider()
st.subheader("🔐 Administrator Access")

if AUTHORIZED_CODE is None:
    st.error(
        "Admin passcode is not configured. "
        "Check your .env file or Streamlit Secrets."
    )

    st.caption(
        f"Expected .env location: {ENV_FILE}"
    )

    st.stop()

password = st.text_input(
    "Enter admin passcode to enable the draw:",
    type="password",
    key="admin_passcode"
)

if password and password_matches(password, AUTHORIZED_CODE):

    st.success("Access granted. Administrator authenticated.")

    # ========================================================
    # 7. EXISTING DRAW: SHOW WINNERS AND RESET OPTION
    # ========================================================

    if WINNER_FILE.is_file():

        st.warning(
            "A lottery draw has already been recorded. "
            "Another draw is disabled until an authorized reset."
        )

        with st.expander("⚙️ Admin Reset Options"):

            st.info(
                "Resetting removes the current winners record "
                "and allows a new draw."
            )

            reset_pass_input = st.text_input(
                "Enter reset password:",
                type="password",
                key="reset_passcode"
            )

            if RESET_PASSWORD is None:
                st.error(
                    "Reset password is not configured. "
                    "Check your .env file or Streamlit Secrets."
                )

            confirm_reset = st.checkbox(
                "I confirm that I want to reset the lottery.",
                key="confirm_reset"
            )

            if st.button(
                "🔄 Reset for New Round",
                key="reset_draw"
            ):

                if RESET_PASSWORD is None:
                    st.error("Reset is unavailable because no reset password is configured.")

                elif not password_matches(
                    reset_pass_input,
                    RESET_PASSWORD
                ):
                    st.error("Incorrect reset password.")

                elif not confirm_reset:
                    st.warning("Please confirm the reset first.")

                else:
                    try:
                        WINNER_FILE.unlink()
                        st.success(
                            "Winners record removed. "
                            "The application is ready for a new draw."
                        )
                        st.rerun()

                    except OSError:
                        st.error(
                            "Unable to remove the winners record. "
                            "Check the folder's file permissions."
                        )

        # Load and display previous winners.
        try:
            previous_winners = pd.read_excel(WINNER_FILE)

            previous_winners = previous_winners.loc[
                :,
                ~previous_winners.columns.astype(str).str.contains(
                    r"^Unnamed",
                    case=False,
                    regex=True
                )
            ].copy()

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

            # Download previous winners.
            previous_output = BytesIO()

            previous_winners.to_excel(
                previous_output,
                index=False,
                engine="openpyxl"
            )

            st.download_button(
                label="💾 Download Previous Winners",
                data=previous_output.getvalue(),
                file_name="EGSA_lottery_winners.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                key="download_previous_winners"
            )

        except Exception:
            st.error(
                "The winners record exists but could not be read. "
                "Check the Excel file before resetting or drawing again."
            )

    # ========================================================
    # 8. NO EXISTING DRAW: SELECT WINNERS
    # ========================================================

    else:

        st.info(
            "No winners record exists. You can conduct the lottery draw."
        )

        num_winners = st.number_input(
            "🏆 Number of winners to select:",
            min_value=1,
            max_value=len(members_df),
            value=1,
            step=1,
            key="number_of_winners"
        )

        if st.button("🎲 Pick Winners", key="pick_winners"):

            # Recheck immediately before drawing.
            if WINNER_FILE.exists():
                st.error(
                    "A winners record already exists. "
                    "The draw has been cancelled."
                )
                st.rerun()

            try:
                with st.spinner("Drawing lottery winners..."):

                    progress_text = st.empty()
                    progress_bar = st.progress(0)

                    for i in range(101):
                        time.sleep(0.01)
                        progress_text.text(f"Progress: {i}%")
                        progress_bar.progress(i)

                    winners = members_df.sample(
                        n=int(num_winners),
                        replace=False
                    ).reset_index(drop=True)

                    winners.insert(
                        0,
                        "No",
                        range(1, len(winners) + 1)
                    )

                    # Prepare the Excel file in memory first.
                    output = BytesIO()

                    winners.to_excel(
                        output,
                        index=False,
                        engine="openpyxl"
                    )

                    # Create the permanent record without
                    # overwriting an existing winners file.
                    with open(WINNER_FILE, "xb") as record_file:
                        record_file.write(output.getvalue())

                progress_text.empty()
                progress_bar.empty()

                st.success("🎉 Winners selected and recorded successfully!")
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
                    ),
                    key="download_new_winners"
                )

            except FileExistsError:
                st.error(
                    "A winners record was created by another process. "
                    "No existing record was overwritten."
                )

            except Exception:
                st.error(
                    "The draw could not be saved. "
                    "Check folder permissions and Excel dependencies "
                    "before trying again."
                )
                st.exception(Exception)

elif password:
    st.error("Invalid passcode. Access denied.")
    st.info(
        "You can view the member list, but only authorized staff "
        "can conduct the lottery draw."
    )
else:
    st.info(
        "Enter the administrator passcode to access the lottery controls."
    )
