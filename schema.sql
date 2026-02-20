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

CREATE TABLE IF NOT EXISTS comic_status(
    comic_status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS authors(
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS comics(
    comic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    comic_description TEXT NOT NULL,
    num_of_chapters INTEGER NOT NULL DEFAULT 1,
    ratings FLOAT DEFAULT 0,
    cover_image TEXT,
    comic_type_id INTEGER,
    comic_status_id INTEGER,
    FOREIGN KEY (comic_type_id) REFERENCES comic_type(comic_type_id),
    FOREIGN KEY(comic_status_id) REFERENCES comic_status(comic_status_id)
);

CREATE TABLE IF NOT EXISTS author_works(
    author_works_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER,
    comic_id INTEGER,
    FOREIGN KEY(author_id) REFERENCES authors(author_id),
    FOREIGN KEY(comic_id) REFERENCES comics(comic_id),
    UNIQUE(author_id, comic_id)
);a

CREATE TABLE IF NOT EXISTS tags(
    tags_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tags_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS comic_tags(
    comic_tags_id INTEGER PRIMARY KEY AUTOINCREMENT,
    comic_id INTEGER,
    tags_id INTEGER,
    FOREIGN KEY (comic_id) REFERENCES comics(comic_id),
    FOREIGN KEY (tags_id) REFERENCES tags(tags_id),
    UNIQUE(comic_id, tags_id)
);

CREATE TABLE IF NOT EXISTS reading_status(
    reading_status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reading_status_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reading_list(
    reading_list_id INTEGER PRIMARY KEY AUTOINCREMENT,
    comic_id INTEGER,
    user_id INTEGER,
    reading_status_id INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY(comic_id) REFERENCES comics(comic_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(reading_status_id) REFERENCES reading_status(reading_status_id),
    UNIQUE(user_id, comic_id)
);