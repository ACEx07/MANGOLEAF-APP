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


def user_rating_exists(user_id, dataset):
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


def user_exists(user_id):
    """
    Check if a user exists in the database

    Parameters
    ----------
    user_id : int
        ID of the user to check

    Returns
    -------
    bool
        True if the user exists, False otherwise
    """
    engine = Connection().get()
    with engine.connect() as connection:
        query = "SELECT * FROM users WHERE user_id = :user_id"
        result = connection.execute(text(query), dict(user_id=user_id)).fetchone()
    return result is not None


def username_exists(username):
    """
    Check if a user exists in the database

    Parameters
    ----------
    username : str
        Username to check

    Returns
    -------
    bool
        True if the user exists, False otherwise
    """
    engine = Connection().get()
    with engine.connect() as connection:
        query = "SELECT * FROM users WHERE username = :username"
        result = connection.execute(text(query), dict(username=username)).fetchone()
    return result is not None


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


def next_user_id():
    """
    Get the next user ID to use

    Returns
    -------
    user_id : int
        Next user ID
    """
    query = "SELECT MAX(user_id) FROM users"
    user_id = pd.read_sql(query, Connection().get()).iloc[0, 0]
    return int(user_id) + 1 if user_id is not None else 0


def list_users_since(date):
    """
    List all active users in the database

    Parameters
    ----------
    date : str
        Date to filter users from

    Returns
    -------
    user_ids : pd.DataFrame
        DataFrame with all active users
    """
    query = """
    SELECT user_id FROM users
    WHERE registered >= %(date)s
    ORDER BY registered ASC
    """
    user_ids = pd.read_sql(query, Connection().get(), params=dict(date=date)).user_id.to_list()
    return user_ids


def register_user(username, password):
    """
    Register a new user in the database

    Parameters
    ----------
    username : str
        Username of the new user

    password : str
        Password of the new user

    Returns
    -------
    success : bool
        True if the registration was successful, False otherwise
    """
    user_id = next_user_id()

    engine = Connection().get()
    with engine.connect() as connection:
        query = """
        INSERT INTO users (user_id, username, password, full_name)
        VALUES (:user_id, :username, :password, :username)
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        connection.execute(
            text(query), dict(username=username, password=hashed_password, user_id=user_id)
        )
        connection.commit()

    # Verify that the user was registered
    return username_exists(username) and user_exists(user_id)


def update_full_name(user_id, new_full_name):
    """
    Update the full name of a user in the database

    Parameters
    ----------
    user_id : int
        ID of the user to update the full name for

    new_full_name : str
        New full name of the user

    Returns
    -------
    success : bool
        True if the update was successful, False otherwise
    """
    engine = Connection().get()
    with engine.connect() as connection:
        query = """
        UPDATE users
        SET full_name = :full_name
        WHERE user_id = :user_id
        """
        connection.execute(text(query), dict(full_name=new_full_name, user_id=user_id))
        connection.commit()

    # Verify that the full name was updated
    success = get_user_info(user_id)["full_name"] == new_full_name
    return success


def update_password(user_id, new_password):
    """
    Update the password of a user in the database

    Parameters
    ----------
    user_id : int
        ID of the user to update the password for

    new_password : str
        New password of the user

    Returns
    -------
    success : bool
        True if the update was successful, False otherwise
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), salt).decode("utf-8")

    engine = Connection().get()
    with engine.connect() as connection:
        query = """
        UPDATE users
        SET password = :password
        WHERE user_id = :user_id
        """
        connection.execute(text(query), dict(password=hashed_password, user_id=user_id))
        connection.commit()

    # Verify that the password was updated
    check = match_user_credentials(get_user_info(user_id)["username"], new_password)
    success = check is not None
    return success


def delete_user(user_id):
    """
    Delete a user from the database

    Parameters
    ----------
    user_id : int
        ID of the user to delete

    Returns
    -------
    success : bool
        True if the deletion was successful, False otherwise
    """
    engine = Connection().get()
    with engine.connect() as connection:
        query = """
        DELETE FROM user_data
        WHERE user_id = :user_id;
        DELETE FROM books_ratings
        WHERE user_id = :user_id;
        DELETE FROM mangas_ratings
        WHERE user_id = :user_id;
        DELETE FROM books_user_based
        WHERE user_id = :user_id;
        DELETE FROM mangas_user_based
        WHERE user_id = :user_id;
        DELETE FROM users
        WHERE user_id = :user_id;
        """
        connection.execute(text(query), dict(user_id=user_id))
        connection.commit()

    # Verify that the user was deleted
    return not user_exists(user_id)


def get_user_info(user_id):
    """
    Get user information from the database

    Parameters
    ----------
    user_id : int
        ID of the user to get the information for

    Returns
    -------
    user_info : dict
        User information
    """
    if user_id is None:
        return dict()
    query = f"""
    SELECT user_id, username, full_name FROM users
    WHERE user_id = {user_id}
    """
    user_info = pd.read_sql(query, Connection().get()).iloc[0].to_dict()
    return user_info


def get_extended_user_info(user_id):
    """
    Get extended user information from the database

    Parameters
    ----------
    user_id : int
        ID of the user to get the information for

    Returns
    -------
    user_info : dict
        Extended user information
    """
    if user_id is None:
        return dict()
    query = f"""
    SELECT user_id, about, registered, image FROM users
    LEFT JOIN user_data USING (user_id)
    WHERE user_id = {user_id}
    """
    user_info = pd.read_sql(query, Connection().get()).iloc[0].to_dict()
    return user_info


def set_user_image(user_id, image):
    """
    Set the user image in the database

    Parameters
    ----------
    user_id : int
        ID of the user to set the image for

    image : bytes
        Image to set
    """
    engine = Connection().get()
    with engine.connect() as connection:
        query = """
        INSERT INTO user_data (user_id, image)
        VALUES (:user_id, :image)
        ON CONFLICT (user_id) DO UPDATE
        SET image = :image
        """
        connection.execute(text(query), dict(user_id=user_id, image=image))
        connection.commit()


def get_num_ratings(user_id):
    """
    Retrieve the number of ratings for a user

    Parameters
    ----------
    user_id : int
        ID of the user to get the number of ratings for

    Returns
    -------
    num_ratings : int
        Number of ratings for the user
    """
    query = f"""
    SELECT COUNT(*) FROM books_ratings
    WHERE user_id = {user_id}
    UNION ALL
    SELECT COUNT(*) FROM mangas_ratings
    WHERE user_id = {user_id}
    """
    num_ratings = pd.read_sql(query, Connection().get()).sum().values[0]
    return num_ratings


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


def export_user_data(user_id):
    """
    Get all user ratings from the database

    Parameters
    ----------
    user_id : int
        ID of the user to get the ratings for

    Returns
    -------
    df : pd.DataFrame
        DataFrame with all user ratings
    """
    query = f"""
    SELECT item_id::text, 'book' as dataset, rating, title, author as secondary FROM books_ratings
    LEFT JOIN books USING (item_id)
    WHERE user_id = {user_id}
    UNION ALL
    SELECT item_id::text, 'manga' as dataset, rating, title, other_title as secondary
        FROM mangas_ratings
    LEFT JOIN mangas USING (item_id)
    WHERE user_id = {user_id}
    """
    df = pd.read_sql(query, Connection().get())
    return df


def get_filtered(dataset, n, user_id, where_query, query_params):
    """
    Get filtered items with rating from the database

    Parameters
    ----------
    dataset : {"books", "mangas"}
        Dataset: "books" or "mangas"

    n : int
        Number of items to load

    user_id : int
        ID of the user to load add the ratings for

    where_query : str
        WHERE query to filter the items

    query_params : dict
        Parameters for the WHERE query

    Returns
    -------
    df : pd.DataFrame
        DataFrame with the filtered items
    """
    if user_id is not None:
        where_query = (
            f"""
        LEFT JOIN (
            SELECT * FROM {dataset}_ratings
            WHERE user_id = {user_id}
        ) r USING (item_id)
        """
            + where_query
        )

    query_str = f"""
    SELECT * FROM {dataset}
    {where_query}
    ORDER BY title
    LIMIT {n};
    """
    df = pd.read_sql(query_str, Connection().get(), params=query_params)
    return df

