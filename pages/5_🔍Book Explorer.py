"""
Books explorer page
"""

from mangoleaf import authentication, frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

frontend.add_header_logo("Book Explorer")

# Filter the DataFrame using the filter function
filter_options = dict(
    title="text",
    author="text",
)
display_names = ["Title", "Author", "Your rating"]

# Add rating if logged in
user_id = authentication.get_user_info()["user_id"]
if user_id is not None:
    filter_options["rating"] = "rating"

frontend.add_explorer("books", user_id, 21, filter_options, display_names)
