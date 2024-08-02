"""
Authenticate user access
"""

import streamlit as st

from mangoleaf import query


def reset():
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.session_state["full_name"] = None
    st.session_state["user_id"] = None


def authenticate(username, password):
    user_info = query.match_user_credentials(username, password)
    if user_info is None:
        return False

    st.session_state["authenticated"] = True
    st.session_state["username"] = user_info["username"]
    st.session_state["full_name"] = user_info["full_name"]
    st.session_state["user_id"] = user_info["user_id"]
    return True


def is_authenticated():
    return st.session_state.get("authenticated", False)


def get_user_info():
    return dict(
        username=st.session_state.get("username", None),
        full_name=st.session_state.get("full_name", None),
        user_id=st.session_state.get("user_id", None),
    )
