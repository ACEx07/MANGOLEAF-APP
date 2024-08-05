"""
Manga explorer page
"""

from mangoleaf import authentication, frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

frontend.add_header_logo("Manga Explorer")

# Filter the DataFrame using the filter function
filter_options = dict(
    title="text",
    other_title="text",
    genres=[
        "comedy",
        "gourmet",
        "adventure",
        "award winning",
        "drama",
        "mystery",
        "sci-fi",
        "fantasy",
        "slice of life",
        "supernatural",
        "romance",
        "horror",
        "suspense",
        "action",
        "ecchi",
        "boys love",
        "sports",
        "avant garde",
        "girls love",
    ],
)
display_names = ["english title", "original title", "genres", "your rating"]

# Add rating if logged in
user_id = authentication.get_user_info()["user_id"]
if user_id is not None:
    filter_options["rating"] = "rating"

frontend.add_explorer("mangas", user_id, 21, filter_options, display_names)
