-- Drop dynamic tables

DROP TABLE IF EXISTS books_ratings CASCADE;
DROP TABLE IF EXISTS mangas_ratings CASCADE;
DROP TABLE IF EXISTS user_data CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Recreate dynamic tables (including constraints)

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) NOT NULL,
  registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_data (
  user_id INTEGER PRIMARY KEY,
  about VARCHAR(255),
  image TEXT,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE books_ratings (
  user_id INTEGER NOT NULL,
  item_id VARCHAR(20) NOT NULL,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  PRIMARY KEY (user_id, item_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (item_id) REFERENCES books(item_id)
);

CREATE TABLE mangas_ratings (
  user_id INTEGER NOT NULL,
  item_id INTEGER NOT NULL,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  PRIMARY KEY (user_id, item_id),
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (item_id) REFERENCES mangas(item_id)
);

-- Copy data from original tables

INSERT INTO users (
  user_id,
  username,
  password,
  full_name,
  registered
)
SELECT * FROM users_original;

INSERT INTO books_ratings (
  user_id,
  item_id,
  rating
)
SELECT * FROM books_ratings_original;

INSERT INTO mangas_ratings (
  user_id,
  item_id,
  rating
)
SELECT * FROM mangas_ratings_original;
