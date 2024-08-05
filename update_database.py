"""
Update the dynamic data with the latest recommendations
"""

from dotenv import load_dotenv

from mangoleaf import Connection, query, recommend


def update_database(users, n=40, count_threshold=50):
    db_engine = Connection().get()
    update_params = dict(con=db_engine, if_exists="replace")

    for dataset in ["books", "mangas"]:
        print(f"Generate recommendations for {dataset}")

        df = recommend.popularity(dataset, n, count_threshold)
        df.to_sql(f"{dataset}_popular", **update_params, index_label="id")

        df = recommend.item_based(dataset, n)
        df.to_sql(f"{dataset}_item_based", **update_params, index=False)

        df = recommend.user_based(dataset, users, n)
        df.to_sql(f"{dataset}_user_based", **update_params, index=False)


if __name__ == "__main__":
    load_dotenv(".streamlit/secrets.toml")

    # Selected users for user-based recommendations
    users = [
        # Manga example users
        1002,
        357,
        2507,
        # Book example users
        114368,
        95359,
        104636,
    ]
    new_users = query.list_users_since("2024-08-01")
    users += new_users

    update_database(users, 40, 50)
