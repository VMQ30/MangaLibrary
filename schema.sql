CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comic_type(
    comic_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comics(
    comic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    comic_description TEXT NOT NULL,
    num_of_chapters INTEGER NOT NULL DEFAULT 1,
    ratings FLOAT,
    comic_type_id INTEGER,
    FOREIGN KEY (comic_type_id) REFERENCES comic_type(comic_type_id)
);

CREATE TABLE IF NOT EXISTS genres(
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comic_genre(
    comic_genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    comic_id INTEGER,
    genre_id INTEGER,
    FOREIGN KEY (comic_id) REFERENCES comics(comic_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
);