"""
User profile
"""

import streamlit as st
from PIL import Image
import io
from mangoleaf import authentication, frontend
import os

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

# Add additional profile information as needed
#st.subheader("Additional Information", anchor=False)
#st.write("You can add more user-specific details here.")


# Profile picture upload

import streamlit as st
import os
from PIL import Image

# Directory to store uploaded images
UPLOAD_FOLDER = 'uploaded_images'

# Ensure the directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def save_image(image_file, user_id):
    """Save the uploaded image to a file."""
    file_path = os.path.join(UPLOAD_FOLDER, f"{user_id}.png")
    with open(file_path, "wb") as f:
        f.write(image_file.getbuffer())
    return file_path

def load_image(user_id):
    """Load the saved image for the user."""
    file_path = os.path.join(UPLOAD_FOLDER, f"{user_id}.png")
    if os.path.exists(file_path):
        return Image.open(file_path)
    return None

def user_profile(user_id):
    """Display the user profile page."""

    # Check if a profile picture exists for the user
    profile_image = load_image(user_id)

    if profile_image is not None:
        # Display the profile picture in a smaller size
        st.image(profile_image, caption='Profile Picture', width=200)
        if st.button("Update your profile picture"):
            # Show the file uploader when the user wants to update the profile picture
            image_file = st.file_uploader("Upload a new profile picture", type=['png', 'jpg', 'jpeg'], key="update")

            if image_file is not None:
                # Save the uploaded image
                save_image(image_file, user_id)
                st.success("Profile picture updated! Please refresh the page.")
    else:
        # Show the file uploader for the first time when no profile picture is uploaded
        image_file = st.file_uploader("Upload a profile picture", type=['png', 'jpg', 'jpeg'], key="upload")

        if image_file is not None:
            # Save the uploaded image
            save_image(image_file, user_id)
            st.success("Profile picture uploaded! Please refresh the page.")

# Sample user 375
user_id = "user_375"  
user_profile(user_id)

st.markdown(f"**Username:** {user_data['username']}")
st.markdown(f"**Name:** {user_data['full_name']}")



