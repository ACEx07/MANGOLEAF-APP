"""
Books explorer page
"""

import pandas as pd
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

from mangoleaf import Connection, frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

col1, col2 = st.columns([1, 7])

with col1:
    st.image("images/mango_logo.png", width=130)

with col2:
    st.title("**BOOK EXPLORER**", anchor=False)

st.markdown(
    """
Have a look through our book database and use filters to find what you are looking for!
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
    modify = st.checkbox("Add filters", key="add_filters_checkbox")

    if not modify:
        return df

    df = df.copy()

    # Try to standardize datetimes (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        # Define which columns can be filtered
        selectable_columns = [
            "item_id",
            "title",
            "author",
            # "Year-Of-Publication",
            # "Publisher",
        ]  # Example columns, adjust as needed

        # Ensure selectable_columns are in df
        selectable_columns = [col for col in selectable_columns if col in df.columns]

        # Use selectable_columns for multiselect
        to_filter_columns = st.multiselect(
            "Filter Books on", selectable_columns, key="filter_columns_multiselect"
        )
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
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
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                    key=f"{column}_num_slider",
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                    key=f"{column}_date_input",
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}", key=f"{column}_text_input"
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


def display_books_with_images(
    df: pd.DataFrame, image_column: str = "image", id_column: str = "item_id"
):
    """
    Display the DataFrame with images using clickable links to the
    books.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to display

    image_column : str
        The column in the DataFrame that contains image URLs

    id_column : str
        The column in the DataFrame that contains the unique IDs
    """

    # Generate HTML with clickable images for display
    def generate_clickable_image_html(row):
        url = f"https://isbnsearch.org/isbn/{row[id_column]}"
        img_html = (
            f"<a href='{url}' rel='noopener noreferrer' target='_blank'>"
            f"<img src='{row[image_column]}' alt='' /></a>"
        )
        return img_html

    # Add a new column for clickable images
    df["image"] = df.apply(generate_clickable_image_html, axis=1)

    # Display the DataFrame with clickable images using HTML
    df_html = df.to_html(
        escape=False,
        columns=[
            "item_id",
            "title",
            "author",
            # "Year-Of-Publication",
            # "Publisher",
            "image",
        ],
        index=False,
    )
    df_html = df_html.replace("<table", '<table class="styled-table"')
    st.markdown(df_html, unsafe_allow_html=True)


# Load the database table into a DataFrame
df = pd.read_sql("books", Connection().get())

# Filter the DataFrame using the filter function
filtered_df = filter_dataframe(df)

# Display the filtered DataFrame with clickable images
display_books_with_images(filtered_df)
