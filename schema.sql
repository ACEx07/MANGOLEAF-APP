DROP TABLE IF EXISTS books_ratings CASCADE;
DROP TABLE IF EXISTS mangas_ratings CASCADE;

DROP TABLE IF EXISTS books_popular CASCADE;
DROP TABLE IF EXISTS mangas_popular CASCADE;
DROP TABLE IF EXISTS books_item_based CASCADE;
DROP TABLE IF EXISTS mangas_item_based CASCADE;
DROP TABLE IF EXISTS books_user_based CASCADE;
DROP TABLE IF EXISTS mangas_user_based CASCADE;

DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS mangas CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- User table (dynamic)

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  full_name VARCHAR(255) NOT NULL
);

-- Book and manga tables (static)

CREATE TABLE books (
  item_id VARCHAR(20) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255),
  image VARCHAR(255)
);

CREATE TABLE mangas (
  item_id INTEGER PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  other_title VARCHAR(255),
  image VARCHAR(255)
);

-- Ratings tables (semi-static)

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
