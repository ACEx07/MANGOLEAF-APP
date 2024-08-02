"""
Functionality for the frontend of repeated tasks
"""

import re

import streamlit as st

from mangoleaf import authentication, query

tv_keywords = re.compile(r"(\s*season\s*\d*\s*|\s*\d*[st|rd|th|\.]*season\s*)", re.IGNORECASE)


def add_config():
    st.set_page_config(
        page_title="Mangoleaf - Book & Manga Recommendations",
        page_icon=":mango:",
        layout="wide",
    )


def add_style():
    with open("style/style.css") as f:
        st.html(f"<style>{f.read()}</style>")


def add_sidebar_logo():
    st.sidebar.image("images/mango_logo.png", use_column_width=True)


def add_user_input(default_user_id):
    user_id = st.text_input(
        "User ID",
        value=str(default_user_id),
        placeholder="Enter your user ID",
    )

    # Convert to integer
    try:
        user_id = int(user_id.strip())
    except ValueError:
        user_id = -1

    return user_id


def format_title(title):
    title = tv_keywords.sub("", title)
    title = title.strip(",. ")
    title = title[0] + title[1:].split("(")[0]
    title = title[0] + title[1:].split(":")[0]
    title = title[0] + title[1:].split("-")[0]
    title = title.strip()
    if len(title) > 20:
        title = title[:20] + "…"
    return title


def add_row_header(heading, context=st):
    context.html(f"<h2 class='row_header'>{heading}</h2>")  # Allow coloring


def make_row_placeholder(n, context=st, skip=None):
    columns = context.columns(n)
    for i, col in enumerate(columns):
        if i == skip:
            continue
        with col:
            st.markdown(
                """<div class="rec_element rec_element_empty">
                    <div></div>
                </div>""",
                unsafe_allow_html=True,
            )


def make_row(df, n, context=st):
    if "author" in df.columns:
        url = "https://isbnsearch.org/isbn/"
    else:
        url = "https://myanimelist.net/anime/"

    html_element = """<div class="rec_element">
        <a href="{url}{item_id}" rel="noopener noreferrer" target="_blank">
            <img src="{img_src}" alt="" class="rec_image">
            <div class="rec_text">
                <p></p>
                <p>{title}</p>
                <p>{secondary}</p>
            </div>
        </a>
    </div>"""

    columns = context.columns(n)
    for i, col in enumerate(columns):
        with col:
            if len(df) <= i:
                st.html("")
                continue
            row = df.iloc[i]
            st.markdown(
                html_element.format(
                    url=url,
                    item_id=row.iloc[0],
                    title=row.iloc[1],
                    secondary=row.iloc[2],
                    img_src=row.iloc[3],
                ),
                unsafe_allow_html=True,
            )


def add_recommendations(dataset, user_id, n):
    # Check if user_id has rated items in that dataset
    user_id_valid = user_id if query.user_exists(user_id, dataset) else None

    # First row
    add_row_header(f"Popular {dataset}")
    first_row = st.empty()
    make_row_placeholder(n, first_row)

    # Second row
    title = dataset
    if user_id_valid is None:
        header = "If you like"
    else:
        header = "Because you read"
    header += " <span class='highlight'>{title}</span> you might also like..."
    second_row_header = st.empty()
    add_row_header(header.format(title=title), second_row_header)
    second_row = st.empty()
    make_row_placeholder(n, second_row)

    # Third row
    add_row_header("Specifically for you")
    third_row = st.empty()
    if user_id is None:
        third_row.warning("Please log in to unlock personal recommendations")
    elif not user_id_valid:
        third_row.warning(f"Start rating {dataset} to unlock personal recommendations")
    else:
        make_row_placeholder(n, third_row)

    def hydrate():
        # First row content
        df = query.popularity(n, dataset, exclude_rated_by=user_id_valid)
        make_row(df, n, first_row)

        # Second row content
        if user_id_valid is not None:
            # Iteratate over items until a valid recommendation is found
            df = []
            attempt = 0
            while len(df) == 0 and attempt < 5:
                ref_item = query.get_random_high_rated(user_id_valid, dataset=dataset)
                title = format_title(ref_item.title)
                add_row_header(header.format(title=title), second_row_header)
                df = query.item_based(ref_item.item_id, n, dataset, exclude_rated_by=user_id_valid)
                attempt += 1
        else:
            # Randomly select reference item from popular items above
            ref_item = df.sample(1).iloc[0]
            title = format_title(ref_item.title)
            add_row_header(header.format(title=title), second_row_header)
            df = query.item_based(ref_item.item_id, n, dataset)
        make_row(df, n, second_row)

        # Third row content
        if user_id_valid is not None:
            df = query.user_based(user_id_valid, n, dataset)
            if len(df) > 0:
                make_row(df, n, third_row)
            else:
                third_row.info(
                    "**All caught up!**  \nStart rating more items to get more recommendations"
                )

    return hydrate


def add_mixed_recommendations(n):
    n_half = n // 2
    n = 2 * n_half  # Make sure n is even

    st.html(
        """<h2 class='row_header' style='display: flex; flex-direction: row;'>
            <div style='flex-grow: 0;'><a href="Books">Popular books</a></div>
            <div style='flex-grow: 1;'></div>
            <div style='flex-grow: 0;'><a href="Manga">Popular mangas</a></div>
    </h2>"""
    )

    html_element = """<div class="rec_element">
        <img src="{img_src}" alt="" class="rec_image">
        <div class="rec_text">
            <p></p>
            <p>{title}</p>
            <p>{secondary}</p>
        </div>
    </div><br>"""

    col_width = [1] * n_half + [0.5] + [1] * n_half
    rec_row = st.empty()
    make_row_placeholder(col_width, rec_row, skip=n_half)

    def hydrate():
        df_books = query.popularity(n_half, "books")
        df_mangas = query.popularity(n_half, "mangas")
        rows = list(df_books.iterrows()) + [(None, None)] + list(df_mangas.iterrows())

        columns = rec_row.columns(col_width)
        for col, (_, row) in zip(columns, rows):
            if row is None:
                continue
            with col:
                st.markdown(
                    html_element.format(
                        item_id=row.iloc[0],
                        title=row.iloc[1],
                        secondary=row.iloc[2],
                        img_src=row.iloc[3],
                    ),
                    unsafe_allow_html=True,
                )

    return hydrate


def add_sidebar_login():
    if authentication.is_authenticated():
        user = authentication.get_user_info()
        st.sidebar.markdown(f"Logged in as {user['username']}")
        if st.sidebar.button("Logout", key="sidebar_logout"):
            authentication.reset()
            st.sidebar.info("You have logged out")
            st.rerun()
    else:
        st.sidebar.title("Login")

        # Sidebar inputs for username and password
        with st.sidebar.form("login_mask", border=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

        # Sidebar button for login
        if submit:
            if authentication.authenticate(username, password):
                user = authentication.get_user_info()
                st.sidebar.success(f"Welcome {user['username']}")
                st.rerun()
            else:
                st.sidebar.error("Username/password is incorrect")

        st.sidebar.info("Please log in to access the content")
