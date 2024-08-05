"""
Generate recommendations based on collaborative filtering
"""

import pandas as pd
from surprise import Dataset, KNNBaseline, Reader
from tqdm import tqdm

from mangoleaf import Connection


def popularity(dataset, n=40, count_threshold=50):
    """
    Generate the most popular items based on ratings

    Parameters
    ----------
    dataset : {"books", "mangas"}
        Name of the dataset to use

    n : int, optional
        Number of items to recommend. Default is 40

    count_threshold : int, optional
        Minimum number of ratings a item must have to be considered.
        Default is 50

    Returns
    -------
    popular : pd.DataFrame
        DataFrame containing the item_ids of the most popular items
    """
    db_engine = Connection().get()

    # Query the most popular items
    query = f"""
    SELECT * FROM {dataset} b
    RIGHT JOIN (
        SELECT item_id, AVG(rating) FROM {dataset}_ratings
        GROUP BY item_id
        HAVING COUNT(rating) > {count_threshold}
    ) as m USING (item_id)
    ORDER BY avg DESC
    LIMIT {n * 2};
    """
    popular = pd.read_sql(query, db_engine).drop(columns="avg")

    # Make the selection diverse by selecting only one item per author
    if "author" in popular.columns:
        popular = popular.drop_duplicates(subset="author")

    popular = popular.head(n).reset_index()

    # Only keep the item_id column
    popular = popular[["item_id"]]

    return popular


def item_based(dataset, n=40):
    """
    Generate item-based recommendations for each item

    Parameters
    ----------
    dataset : {"books", "mangas"}
        Name of the dataset to use

    n : int, optional
        Number of items to recommend. Default is 40

    Returns
    -------
    item_based : pd.DataFrame
        DataFrame containing recommended item_ids for all item_ids
    """
    # Load all the ratings
    ratings = pd.read_sql(f"SELECT * FROM {dataset}_ratings", Connection().get())

    # Load data into surprise
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings, reader)

    # Create item-based collaborative filtering model
    options = dict(
        k=40,
        min_k=1,
        sim_options=dict(
            name="pearson_baseline",
            user_based=False,
        ),
    )
    algo = KNNBaseline(**options)
    full_train = data.build_full_trainset()
    algo.fit(full_train)

    # Get the top nearest neighbors
    item_list = dict()
    for item_id in tqdm(ratings.item_id.unique()):
        inner_id = algo.trainset.to_inner_iid(item_id)
        neighbors = algo.get_neighbors(inner_id, k=n)
        item_list[item_id] = [algo.trainset.to_raw_iid(inner_id) for inner_id in neighbors]

    item_based = pd.DataFrame(item_list).T.reset_index(names="item_id")
    return item_based


def user_based(dataset, users, n=40):
    """
    Generate user-based recommendations selected users

    Parameters
    ----------
    dataset : {"books", "mangas"}
        Name of the dataset to use

    users : list
        List of user_ids to generate recommendations for

    n : int, optional
        Number of items to recommend. Default is 40

    Returns
    -------
    user_based : pd.DataFrame
        DataFrame containing recommended item_ids for selected user_ids
    """
    # Load all the ratings
    ratings = pd.read_sql(f"SELECT * FROM {dataset}_ratings", Connection().get())

    # Load data into surprise
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(ratings, reader)

    # Create item-based collaborative filtering model
    options = dict(
        k=40,
        min_k=1,
        sim_options=dict(
            name="pearson_baseline",
            user_based=True,
        ),
    )
    algo = KNNBaseline(**options)
    full_train = data.build_full_trainset()
    algo.fit(full_train)

    # Create set for predictions
    testset = full_train.build_anti_testset()

    # Predict recommendations based on specific users
    user_list = dict()
    for user_id in tqdm(users):
        filtered_testset = [row for row in testset if row[0] == user_id]
        if len(filtered_testset) == 0:
            continue
        predictions = algo.test(filtered_testset)
        pred = pd.DataFrame(predictions).nlargest(n, "est")
        user_list[user_id] = pred["iid"].to_list()

    user_based = pd.DataFrame(user_list).T.reset_index(names="user_id")
    return user_based
