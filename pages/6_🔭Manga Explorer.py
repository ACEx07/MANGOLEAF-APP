"""
Manga explorer page
"""

import pandas as pd
import streamlit as st
from pandas.api.types import is_numeric_dtype

from mangoleaf import Connection, authentication, frontend, query

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

col1, col2 = st.columns([1, 7])

with col1:
    st.image("images/mango_logo.png", width=130)

with col2:
    st.title("**MANGA EXPLORER**", anchor=False)

st.markdown(
    """
Have a look through our manga database and use filters to find what you are looking for!
"""
)


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a DataFrame to let viewers filter columns

    Parameters
    ----------
    df : pd.DataFrame
        Original DataFrame

    Returns
    -------
    df : pd.DataFrame
        Filtered DataFrame
    """
    df = df.copy()

    with st.container(border=True):
        # Define which columns can be filtered
        selectable_columns = [
            "title",
            # "Genres",
            # "Rank",
            # "Score",
            "other_title",
        ]

        for column in selectable_columns:
            # Treat columns with < 10 unique values as categorical
            if isinstance(df[column], pd.CategoricalDtype) or df[column].nunique() < 10:
                user_cat_input = st.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                    key=f"{column}_cat_multiselect",
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = st.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                    key=f"{column}_num_slider",
                )
                df = df[df[column].between(*user_num_input)]
            else:
                column_desc = column.replace("_", " ").capitalize()
                user_text_input = st.text_input(
                    f"Search {column_desc}",
                    key=f"{column}_text_input"
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


user_id = authentication.get_user_info()["user_id"]


def update_rating(item_id, rating_before, key):
    rating = st.session_state.get(key)
    if rating is not None:
        rating = (rating + 1) * 2
        print(f"User {user_id} updated rating for {item_id} from {rating_before} to {rating}")
        query.update_rating("mangas", user_id, item_id, rating)


# Load the database table into a DataFrame
if user_id is None:
    query_str = """
    SELECT * FROM mangas
    ORDER BY item_id
    LIMIT 21; -- For testing only
    """
else:
    query_str = f"""
    SELECT * FROM mangas
    LEFT JOIN mangas_ratings USING (item_id)
    WHERE user_id = {user_id}
    ORDER BY item_id
    LIMIT 21; -- For testing only
    """
df = pd.read_sql(query_str, Connection().get())

# Filter the DataFrame using the filter function
filtered_df = filter_dataframe(df)

st.html("<br>")

outer_columns = st.columns(3)
for idx, (_, row) in enumerate(filtered_df.iterrows()):
    col1, col2 = outer_columns[idx % 3].columns([1, 3])
    item = f"""
        <div class="rec_element">
            <a href="https://myanimelist.net/anime/{row['item_id']}" rel="noopener noreferrer"
               target="_blank">
                <img src="{row['image']}" alt="" class="rec_image">
                <div class="rec_text">
                    <p></p>
                    <p>{row['title']}</p>
                    <p>{row['other_title']}</p>
                </div>
            </a>
        </div>
    </div>
    """
    col1.html(item)
    col2.markdown(f"**{row["title"]}**  \n{row["other_title"]}")
    key = f"rate_{row["item_id"]}"

    if row.get("rating") is not None:
        st.session_state[key] = (row["rating"] // 2) - 1
    col2.feedback(
        "stars", key=key, on_change=update_rating, args=(row["item_id"], row.get("rating"), key),
        disabled=user_id is None
    )
    if user_id is None:
        col2.markdown("Log in to rate")
