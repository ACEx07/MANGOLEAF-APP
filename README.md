<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="images/white_logo_transparent_background.png">
  <source media="(prefers-color-scheme: light)" srcset="images/black_logo_transparent_background.png">
  <img alt="Mangoleaf" src="images/black_logo_transparent_background.png">
</picture>

[![streamlit](https://img.shields.io/badge/streamlit-deployed-4c1?logo=streamlit&logoColor=white)](https://mangoleaf-dev.streamlit.app)

Welcome to MANGOLEAF, your ultimate guide to discovering the best books and manga tailored to your tastes.
Whether you're a seasoned reader or just starting, MANGOLEAF provides personalized recommendations to help you find your next favorite read.

Personal recommendations for books and mangas implemented using collaborative filtering based recommender systems (popularity, user-based & item-based).

---

<a href="https://github.com/user-attachments/assets/b0deb0a2-7918-4bd3-aa52-b936915b2abc" target="_blank"><img src="https://github.com/user-attachments/assets/abb83a94-6ab0-424c-af95-d77cf288de1e" alt="" width="40%" /></a>
&nbsp;
<a href="https://github.com/user-attachments/assets/7b9276b8-dd56-43ae-b127-d819762d3093" target="_blank"><img src="https://github.com/user-attachments/assets/38233220-5045-4e95-a7e2-933111a556a2" alt="" width="40%" /></a>
<br />
<a href="https://github.com/user-attachments/assets/46ad716d-2336-44ba-9b8b-6ed6cc868ce7" target="_blank"><img src="https://github.com/user-attachments/assets/18dfe85f-3621-44fc-a07b-0d09bf57d526" alt="" width="40%" /></a>
&nbsp;
<a href="https://github.com/user-attachments/assets/1a4f6d30-4922-4538-9b3c-9f8e4cb009ac" target="_blank"><img src="https://github.com/user-attachments/assets/e9e43d70-ebe9-4fd9-a001-8f3098e4335c" alt="" width="40%" /></a>
</div>

## Authors

[![Contributors](https://contrib.rocks/image?repo=szapp/Mangoleaf)](https://github.com/szapp/Mangoleaf/graphs/contributors)

## Project

The goal of this project was to familiarize ourselves with and develop different recommender systems during a limited time of 2.5 weeks and clearly defined deliverable using agile methods.
The recommender systems include item popularity based, item-based collaborative filtering, and user-based collaborative filtering.

The deliverable is a functional web app including user profiles for personalized recommendation available to anyone.
For the sake of demonstration the datasets are limited to around 2000 items (around 1500 books and 500 manga) and the personalized recommendations are updated only at certain intervals (every 24 hours).

To avoid spam and abuse in this demo project, user ratings are reset and user profiles are deleted every five days.
To offset this limitation, user ratings can be exported and downloaded as CSV file at any time.

## Key learning

- Project planning and collaborative work using agile methods
- Balancing limited time against a working product
- Working with different datasets and bring them into a consistent format
- Deploying a Streamlit app online
- Implementing and maintain a PostgreSQL database
- Implementing user authentication with hashed and salted passwords and base64-encoded, cropped user pictures
- Automated scheduling with GitHub Action workflows

## Languages, Tools, and Libraries

- scikit-surprise
- streamlit
- pandas
- SQLAlchemy
- bcrypt
- pillow
- Postgres SQL

<sup><i>See [requirements.txt](requirements.txt) for all used Python packages.</i></sup>

## Schedule

The project was implemented based on a well devised schedule of two and a half weeks.
Implementation was done using agile methods including daily stand-ups, iterative implementations of minimally working examples, and weekly sprints/milestones.

<div align="center">
<picture>

  ![schedule](https://github.com/user-attachments/assets/13da011d-cd98-4512-b429-06d3ed1d9869)
</picture>
</div>

## Data sources

The datasets fueling the recommendations were modified from

- https://www.kaggle.com/datasets/arashnic/book-recommendation-dataset
- https://www.kaggle.com/datasets/dbdmobile/myanimelist-dataset

The repository [szapp/Mangoleaf](https://github.com/szapp/Mangoleaf) is an adjacent implementation.
