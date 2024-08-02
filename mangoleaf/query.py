"""
Query the current recommendations from the database.

This file does not compute any recommendations, it only loads the
precomputed recommendations from the SQL database. The recommendations
are then displayed in the streamlit app.
"""

import bcrypt
import pandas as pd
from sqlalchemy.sql import text

from mangoleaf import Connection


def popularity(n, dataset, exclude_rated_by=None):
    """
    Popular books or mangas recommender.

    Parameters
    ----------
    n : int
        Number of books or mangas to recommend

    dataset : str
        Dataset: "books" or "mangas"

    exclude_rated_by : int, optional
        Exclude books or mangas that have been rated by this user

    Returns
    -------
    pd.DataFrame
        DataFrame with the top n most popular books or mangas
    """
    query = f"""
    SELECT * FROM {dataset}_popular
    INNER JOIN {dataset} USING(item_id)
    WHERE item_id NOT IN (
        SELECT item_id FROM {dataset}_ratings WHERE user_id = {exclude_rated_by or -1}
    )
    ORDER BY id
    LIMIT {n};
    """
    df = pd.read_sql(query, Connection().get(), index_col="id")
    return df


def item_based(item_id, n, dataset, exclude_rated_by=None):
    """
    Item-based collaborative filtering recommender.

    Parameters
    ----------
    item_id : str
        ISBN or anime_id of the book or manga to base recommendations on

    n : int
        Number of books or mangas to recommend

    dataset : str
        Dataset: "books" or "manga"

    exclude_rated_by : int, optional
        Exclude books or mangas that have been rated by this user

    Returns
    -------
    pd.DataFrame
        DataFrame with the top n recommended books or mangas
    """
    query = f"""
    SELECT * FROM {dataset}_item_based
    WHERE item_id = '{item_id}'
    LIMIT 1;
    """
    item_ids = pd.read_sql(query, Connection().get(), index_col="item_id").squeeze().to_list()

    query = f"""
    SELECT * FROM {dataset}
    WHERE item_id IN ({", ".join([f"'{i}'" for i in item_ids])})
    AND item_id NOT IN (
        SELECT item_id FROM {dataset}_ratings
        WHERE user_id = {exclude_rated_by or -1}
    );
    """
    df = pd.read_sql(query, Connection().get(), index_col="item_id")
    item_ids = [i for i in item_ids if i in df.index]
    df = df.loc[item_ids].reset_index().head(n)
    return df


def user_based(user_id, n, dataset="books"):
    """
    User-based collaborative filtering recommender.

    Parameters
    ----------
    user_id : int
        ID of the user to base recommendations on

    n : int
        Number of books or mangas to recommend

    dataset : str
        Dataset: "books" or "manga"

    Returns
    -------
    pd.DataFrame
        DataFrame with the top n recommended books or mangas
    """
    query = f"""
    SELECT * FROM {dataset}_user_based
    WHERE user_id = '{user_id}'
    LIMIT 1;
    """
    item_ids = pd.read_sql(query, Connection().get(), index_col="user_id").squeeze()
    if item_ids.empty:
        return pd.DataFrame()
    item_ids = item_ids.to_list()

    query = f"""
    SELECT * FROM {dataset}
    WHERE item_id IN ({", ".join([f"'{i}'" for i in item_ids])});
    """
    df = pd.read_sql(query, Connection().get(), index_col="item_id")
    item_ids = [i for i in item_ids if i in df.index]
    df = df.loc[item_ids].reset_index().head(n)
    return df


def get_random_high_rated(user_id, dataset):
    """
    Get a random high rated book or manga from the user's history

    Parameters
    ----------
    user_id : int
        ID of the user to get the book or manga from

    dataset : str
        Dataset: "books" or "manga"

    Returns
    -------
    pd.Series
        Item information of the random high rated book or manga
    """
    query_user = f"WHERE user_id = {user_id}" if user_id is not None else ""
    query = f"""
    SELECT * FROM {dataset}_ratings
    INNER JOIN {dataset} USING (item_id)
    {query_user}
    ORDER BY rating DESC, RANDOM()
    LIMIT 10;
    """
    ratings = pd.read_sql(query, Connection().get())
    df = ratings.sample(1).drop(columns=["user_id", "rating"]).iloc[0]
    return df


def user_exists(user_id, dataset):
    """
    Check if a user exists in the dataset

    Parameters
    ----------
    user_id : int
        ID of the user to check

    dataset : str
        Dataset: "books" or "manga"

    Returns
    -------
    bool
        True if the user exists, False otherwise
    """
    if user_id is None:
        return False
    query = f"""
    SELECT * FROM {dataset}_ratings
    WHERE user_id = {user_id}
    """
    df = pd.read_sql(query, Connection().get())
    return len(df) > 0


def match_user_credentials(username, password):
    """
    Check if username and password match credentials in database

    Parameters
    ----------
    username : str
        Username to check

    password : str
        Password to check

    Returns
    -------
    user_info : dict or None
        User information if the credentials match, None otherwise
    """
    engine = Connection().get()
    with engine.connect() as connection:
        query = text("SELECT * FROM users WHERE username = :username")
        result = connection.execute(query, dict(username=username)).fetchone()

        if result is None:
            return None

        if not bcrypt.checkpw(password.encode("utf-8"), result.password.encode("utf-8")):
            return None

        user_info = dict(result._mapping)
    return user_info


def update_rating(dataset, user_id, item_id, rating):
    """
    Update the rating of a book or manga in the database

    Parameters
    ----------
    dataset : {"books", "mangas"}
        Dataset: "books" or "mangas"

    user_id : int
        ID of the user to update the rating for

    item_id : str
        ISBN or anime_id of the book or manga to update the rating for

    rating : {1, 2, 3, 4, 5}
        New rating for the book or manga
    """
    engine = Connection().get()
    with engine.connect() as connection:
        query = f"""
        INSERT INTO {dataset}_ratings (user_id, item_id, rating)
        VALUES (:user_id, :item_id, :rating)
        ON CONFLICT (user_id, item_id) DO UPDATE
        SET rating = :rating
        """
        connection.execute(text(query), dict(user_id=user_id, item_id=item_id, rating=rating))
        connection.commit()
