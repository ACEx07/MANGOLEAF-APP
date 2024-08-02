"""
Update the dynamic data with the latest recommendations
"""

from mangoleaf import Connection, recommend


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
    # Selected users for user-based recommendations
    users = [
        # Mangas
        1002,
        357,
        2507,
        # Books
        114368,
        95359,
        104636,
    ]
    update_database(users, 40, 50)
