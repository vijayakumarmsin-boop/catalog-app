import streamlit as st
import pandas as pd

def check_login():

    # Load users from Excel (NO MySQL)
    try:
        users_df = pd.read_excel("users.xlsx")
    except Exception:
        st.error("users.xlsx file not found")
        st.stop()

    # Clean column names
    users_df.columns = users_df.columns.str.strip().str.lower()

    # session state init
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "role" not in st.session_state:
        st.session_state.role = None

    if "username" not in st.session_state:
        st.session_state.username = None

    if not st.session_state.logged_in:

        # UI layout
        left, center, right = st.columns([2, 1, 2])

        with center:

            st.markdown("<br><br><br>", unsafe_allow_html=True)

            with st.container(border=True):

                st.markdown(
                    """
                    <h2 style='text-align:center; margin-bottom:20px;'>
                    🔐 LOGIN
                    </h2>
                    """,
                    unsafe_allow_html=True
                )

                username = st.text_input("", placeholder="Username")
                email = st.text_input("", placeholder="Email ID")

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("Login", use_container_width=True):

                    # match user
                    user_match = users_df[
                        (users_df["username"].str.strip().str.lower() == username.strip().lower()) &
                        (users_df["email"].str.strip().str.lower() == email.strip().lower())
                    ]

                    if not user_match.empty:

                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.email = email
                        st.session_state.role = user_match.iloc[0]["role"]

                        st.success("Login Success")
                        st.rerun()

                    else:
                        st.error("Invalid Username or Email")

        st.stop()