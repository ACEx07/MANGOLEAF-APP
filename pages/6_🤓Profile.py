"""
User profile
"""

from datetime import datetime
from time import sleep

import streamlit as st

from mangoleaf import authentication, frontend, query

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

frontend.add_header_logo("User Profile")

# Check if the user is authenticated
if not authentication.is_authenticated():
    st.warning("Please log in from the home page to access this page.")
    st.stop()  # Stop further execution if not authenticated

# Get user information
user_data = authentication.get_user_info()
user_id = user_data["user_id"]
username = user_data["username"]
full_name = user_data["full_name"]
registered = user_data.get("registered")

# Get number of ratings
items_rated = query.get_num_ratings(user_id)

if isinstance(registered, datetime):
    days_registered = (datetime.now().date() - registered.date()).days
    if days_registered == 0:
        member_since = "Registered today"
    elif days_registered == 1:
        member_since = "Registered yesterday"
    elif days_registered < 4:
        member_since = f"Registered {days_registered} days ago"
    elif days_registered < 8:
        member_since = "Registered this week"
    else:
        member_since = "Registered " + registered.strftime("%Y-%m-%d")
else:
    member_since = ""

# Profile card
profile_card_html = f"""
<div class="profile_card_container">
    <div class="profile_card_overflow"></div>
    <div class="profile_card_image_container">{{content}}</div>
    <div class="profile_card_info_container">
        <div>{full_name}</div>
        <div>{username}</div>
        <div>{member_since}</div>
        <div>Items rated: {items_rated}</div>
    </div>
</div>
"""
image_html = "<img src='data:image/png;base64,{profile_image}' alt=''>"
placeholder_html = "<div class='img_placeholder'><div>No picture</div></div>"
loading_html = "<div class='img_loading'><div></div></div>"

# Placeholder for the profile card to be dynamically updated
profile_card = st.empty()


@st.fragment
def image_operation():
    """This is enclosed in a fragment to prevent reloading the page"""
    profile_image = frontend.load_profile_image(user_id)

    if profile_image:
        profile_card.html(
            profile_card_html.format(content=image_html.format(profile_image=profile_image))
        )

        if st.button("Remove Profile Picture"):
            query.set_user_image(user_id, None)
            st.rerun(scope="fragment")
    else:
        profile_card.html(profile_card_html.format(content=placeholder_html))
        if frontend.upload_profile_image(user_id):
            st.rerun(scope="fragment")


st.html("<br />")
with st.container(border=True):

    # Change full_name
    profile_card.html(profile_card_html.format(content=loading_html))
    new_full_name = st.text_input(
        "Change your name",
        full_name,
        max_chars=50,
        key="new_name",
    )
    del st.session_state["new_name"]
    if new_full_name != full_name:
        success = authentication.update_full_name(user_id, new_full_name)
        if success is True:
            st.rerun()
        elif success == "name_short":
            st.warning("Name must be at least 5 characters long.")
        else:
            st.error("An error occurred while updating your name.")

    # Change password
    new_password = st.text_input(
        "Change your password",
        "",
        placeholder="*****",
        type="password",
        max_chars=50,
        key="new_password",
    )
    del st.session_state["new_password"]  # For safety
    if new_password:
        min_length = 8
        success = authentication.update_password(user_id, new_password, min_length)
        if success is True:
            st.rerun()
        elif success == "password_short":
            st.warning("Password must be at least {min_length} characters long.")
        else:
            st.error("An error occurred while updating your password.")

    # Update or delete user picture
    image_operation()

    # Delete account
    delete_account = st.text_input(
        "Permanently delete your account (type 'delete' to confirm)",
        "",
        max_chars=6,
        placeholder="delete",
        key="delete_account",
    )
    del st.session_state["delete_account"]
    if delete_account:
        success = query.delete_user(user_id)
        if not success:
            st.error("An error occurred while deleting your user account.")
        else:
            authentication.reset()
            st.success("Your account has been deleted.")
            with st.spinner("Logging you out..."):
                sleep(3)
                st.rerun()
st.html("<br />")

# Download data
if st.button("Export your ratings"):
    df = query.export_user_data(user_id)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Press to Download",
        csv,
        f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}_user_data_{username}.csv",
        "text/csv",
        key="download_user_data",
    )

# Logout button
if st.button("Logout"):
    authentication.reset()
    st.success("You have logged out.")
    st.rerun()
