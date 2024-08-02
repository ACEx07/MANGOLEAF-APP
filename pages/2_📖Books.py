"""
Book recommendation page
"""

import streamlit as st

from mangoleaf import authentication, frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

st.image("images/book_logo_transparent_background.png", width=530)

user_info = authentication.get_user_info()
hydrate_recommendations = frontend.add_recommendations("books", user_info["user_id"], n=8)

# In the very end, we hydrate the recommendations
hydrate_recommendations()
