"""
Functionality for the frontend of repeated tasks
"""

import re

import pandas as pd
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


def add_header_logo(header):
    col1, col2 = st.columns([1, 7])
    col1.image("images/mango_logo.png", width=130)
    col2.title(f"**{header.upper()}**", anchor=False)


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


def filter_builder(filter_options, display_names=None):
    """
    Adds filter options for the user to query the database

    Parameters
    ----------
    filter_options : dict
        Mapping of column names to select for filtering and their filter
        type, either "text", "rating", or a tuple/list of categories for
        a multiselect

    display_names : list, optional
        List of display names for the columns in the filter. Defaults to
        the table column names

    Returns
    -------
    where_query : str
        Partial SQL query to filter the database (WHERE clause)

    query_params : dict
        Mapping of query parameters to pass to the SQL query
    """
    clauses = []
    query_params = {}
    if display_names is None:
        display_names = list(filter_options.keys())
    with st.container(border=True):
        for (column, filter_type), disp_name in zip(filter_options.items(), display_names):

            assert column.find(" ") == -1, "Column names cannot contain spaces"

            if isinstance(filter_type, str) and filter_type == "text":
                # Text search
                user_text_input = st.text_input(f"Search {disp_name}", key=f"{column}_text_input")
                if user_text_input:
                    query_params[column] = f"%{user_text_input}%"
                    clauses.append(column + f" LIKE %({column})s")
            elif isinstance(filter_type, str) and filter_type == "rating":
                # Numeric range slider
                col1, col2 = st.columns(2, gap="large", vertical_alignment="center")
                user_num_input = col1.slider(
                    "Range of your rating",
                    min_value=1,
                    max_value=5,
                    value=(1, 5),
                    step=1,
                    key=f"{column}_num_slider",
                )
                user_bool_input = col2.checkbox(
                    "Include unrated",
                    value=True,
                    key=f"{column}_bool_checkbox",
                )
                query_params[f"{column}_min"] = int(user_num_input[0])
                query_params[f"{column}_max"] = int(user_num_input[1])
                if user_bool_input:
                    clauses.append(
                        "(" + column + f" BETWEEN %({column}_min)s AND %({column}_max)s"
                        " OR " + column + " IS NULL)"
                    )
                else:
                    clauses.append(column + f" BETWEEN %({column}_min)s AND %({column}_max)s")
            else:
                # Categorical values
                filter_type = list(map(str, filter_type))
                user_cat_input = st.multiselect(
                    f"Categories of {disp_name}",
                    filter_type,
                    default=filter_type,
                    key=f"{column}_cat_multiselect",
                )
                query_params[column] = tuple(user_cat_input)
                clauses.append(column + f" IN %({column})s")

    where_query = " AND ".join(clauses)
    if where_query:
        where_query = "WHERE " + where_query
    return where_query, query_params


def update_rating(dataset, user_id, item_id, rating_before, key):
    """
    Update the user rating in the database

    Parameters
    ----------
    dataset : {"books", "mangas"}
        Database to update the rating in

    user_id : int
        User ID to update the rating for

    item_id : int
        Item ID to update the rating for

    rating_before : int
        Previous rating before the update

    key : str
        Session state key for the rating
    """
    rating = st.session_state.get(key, pd.NA)
    if not pd.isna(rating):
        rating += 1
        if rating != rating_before:
            query.update_rating(dataset, user_id, item_id, rating)
            st.toast("Rating updated", icon="⭐")


def add_explorer(dataset, user_id, n, filter_options, display_names=None):
    """
    Add the explorer for the database

    Parameters
    ----------
    dataset : {"books", "mangas"}
        Database to explore

    user_id : int
        User ID to get the ratings for

    n : int
        Maximum number of items to display

    filter_options : dict
        Mapping of column names to select for filtering and their filter

    display_names : list, optional
        List of display names for the columns in the filter. Defaults
        to the column names
    """
    st.markdown(
        f"Have a look through our {dataset[:-1]} database and use filters "
        "to find what you are looking for!"
    )

    # Filter the database
    where_query, query_params = filter_builder(filter_options, display_names)
    df = query.get_filtered(dataset, n, user_id, where_query, query_params)

    # Fill the ratings
    for _, row in df.iterrows():
        if not pd.isna(row.get("rating", pd.NA)):
            key = f"rate_{row['item_id']}"
            st.session_state[key] = row["rating"] - 1

    # Check for empty results
    st.html("<br>")
    if len(df) <= 0:
        st.html(
            """
        <div class="explorer_info">
            <div>No items found with the given filters.</div>
        </div>
        """
        )
        return

    # HTML elements for the items
    if "author" in df.columns:
        url = "https://isbnsearch.org/isbn/"
    else:
        url = "https://myanimelist.net/anime/"
    html_element = """
        <div class="rec_element">
            <a href="{url}{item_id}" rel="noopener noreferrer" target="_blank">
                <img src="{img_src}" alt="" class="rec_image">
                <div class="rec_text">
                    <p></p>
                    <p>{title}</p>
                    <p>{secondary}</p>
                </div>
            </a>
        </div>
    </div>
    """

    # Add the items in a grid
    outer_columns = st.columns(3)
    for idx, (_, row) in enumerate(df.iterrows()):
        col1, col2 = outer_columns[idx % 3].columns([1, 3])

        col1.html(
            html_element.format(
                url=url,
                item_id=row["item_id"],
                title=row["title"],
                secondary=row.iloc[2],
                img_src=row["image"],
            )
        )
        col2.markdown(f"**{row['title']}**  \n{row.iloc[2]}")
        key = f"rate_{row['item_id']}"
        col2.feedback(
            "stars",
            key=key,
            on_change=update_rating,
            args=(dataset, user_id, row["item_id"], row.get("rating", pd.NA), key),
            disabled=user_id is None,
        )
        if user_id is None:
            col2.markdown("Log in to rate")

    # Add note about limited results
    if len(df) >= n:
        st.html(
            f"""
        <div class="explorer_info">
            <div>Showing the first {n} results. Refine your search to see more.</div>
        </div>
        """
        )


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
