"""
Contact form
"""

import os

import streamlit as st

from mangoleaf import frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

frontend.add_header_logo("Contact")

st.title("**We'd Love to Hear from You!**", anchor=False)

st.markdown(
    """
Are you passionate about books and manga? Have questions, feedback, or suggestions for us? Whether
you're looking for the next great read or have some thoughts on our recommendations, we're here to
listen. Max and Sören, our dedicated data scientists, are constantly working to enhance your
reading experience. Your input is invaluable to us.

Drop us a message below, and let's start a conversation!
"""
)

st.header(":mailbox: Get In Touch With Us!", anchor=False)

contact_form = f"""
<form action="https://formsubmit.co/{os.environ.get('CONTACT_EMAIL', '')}" method="POST">
     <input type="hidden" name="_captcha" value="false">
     <input type="text" name="name" placeholder="Your name" required>
     <input type="email" name="email" placeholder= "Your email" required>
     <textarea name="message" placeholder="Your message here"></textarea>
     <button type="submit">Send</button>
</form>
"""
st.html(contact_form)

st.image("images/mango_reading.png", width=550)
