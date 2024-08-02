"""
User profile
"""

import streamlit as st

from mangoleaf import authentication, frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

col1, col2 = st.columns([1, 7])

with col1:
    st.image("images/mango_logo.png", width=130)

# Display user profile information
with col2:
    st.title("**USER PROFILE**", anchor=False)

# Check if the user is authenticated
if not authentication.is_authenticated():
    st.warning("Please log in from the home page to access this page.")
    st.stop()  # Stop further execution if not authenticated

user_data = authentication.get_user_info()

st.markdown(f"**Username:** {user_data['username']}")
st.markdown(f"**Name:** {user_data['full_name']}")

# Add additional profile information as needed
st.subheader("Additional Information", anchor=False)
st.write("You can add more user-specific details here.")

if st.button("Logout"):
    authentication.reset()
    st.success("You have logged out.")
    st.rerun()
