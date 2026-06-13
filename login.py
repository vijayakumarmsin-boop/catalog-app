import streamlit as st
import pandas as pd
import mysql.connector


def check_login():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="catalog123",
        database="catalogue_db"
    )

    users_df = pd.read_sql("SELECT * FROM users", conn)
    conn.close()

    users_df.columns = users_df.columns.str.strip().str.lower()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "role" not in st.session_state:
        st.session_state.role = None

    if not st.session_state.logged_in:

        # CENTER LAYOUT
        left, center, right = st.columns([2, 1, 2])

        with center:

            # TOP SPACING
            st.markdown("<br><br><br>", unsafe_allow_html=True)

            # LOGIN BOX
            with st.container(border=True):

                st.markdown(
                    """
                    <h2 style='text-align:center; margin-bottom:20px;'>
                    🔐 LOGIN
                    </h2>
                    """,
                    unsafe_allow_html=True
                )

                username = st.text_input(
                    "",
                    placeholder="Username"
                )

                email = st.text_input(
                    "",
                    placeholder="Email ID"
                )

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button("Login", use_container_width=True):

                    user_match = users_df[
                        (users_df["username"].str.strip().str.lower() ==
                         username.strip().lower()) &
                        (users_df["email"].str.strip().str.lower() ==
                         email.strip().lower())
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