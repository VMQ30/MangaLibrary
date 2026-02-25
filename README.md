# MangaQuery

### Video Demo: https://www.canva.com/design/DAHCPqCQm3w/O2sEOhphpyq4e8z0s7E1KA/edit?utm_content=DAHCPqCQm3w&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

### Description:

MangaVault is a single-page web application designed for manga, manhwa, and manhua enthusiasts who want a centralized place to discover new titles, maintain reading lists, and contribute their own entries to a growing catalog. The project was built entirely with Flask, HTML, CSS, and JavaScript and data is stored in the database though Sqlite3. The goal was to create an application that feels polished while remaining useful and illed with functionalities useful for its main purpose.

The comic tracking space is dominated by large platforms that require accounts, load slowly, and bombard users with ads. MangaVault takes a different approach. It is a user first website and focues on the user's experience. With no adds and plenty of flexibility, it focuses on the user's enjoyment and ease of use when tracking all of their reading lists for comcis.

## Project Structure and File Descriptions

The entry point is `app.py`, which configures the Flask application, initializes the database, and registers all route handlers. Session management is handled by Flask-Session with filesystem-backed storage, and passwords are hashed using Werkzeug's `generate_password_hash` and `check_password_hash` utilities, ensuring credentials are never stored in plain text.

### Core Application Logic (`app.py`)

Database Initialization (`init_db`) runs automatically on startup and checks whether `manga_query.db` exists. If it does not, the function reads and executes `schema.sql` to create the full table structure, then seeds four reference tables: `reading_status` (Reading, Completed, Plan to Read), `comic_type` (Manwha, Manga, Manhua), `comic_status` (Ongoing, Completed, Hiatus), and `tags` (twenty genre tags ranging from Action and Fantasy to Villainess and Post-Apocalyptic). This approach ensures the application is always in a usable state on first launch without requiring manual database setup.

db_execute(q, \*args) is the centralized database helper that opens a connection, executes a parameterized query, commits writes, returns rows for SELECT statements, and guarantees the connection is closed via a `finally` block. Every database interaction in the application flows through this single function, which keeps connection management consistent and makes future migration to a different database straightforward.

login_required(f) is a decorator applied to all routes that require authentication. It checks `session["user_id"]` and redirects unauthenticated users to `/login`. This pattern keeps authorization logic DRY and ensures no protected route can accidentally be accessed without a valid session.

###Routes
/home renders the landing page and clears any existing session, ensuring visitors start fresh. The landing page serves as the marketing entry point, and clearing the session prevents stale authentication state from persisting across visits.

/register handles user registration. On GET, it renders the authentication template. On POST, it validates that email and password are present, hashes the password with Werkzeug's PBKDF2 implementation, and inserts the new user into the `users` table. The `INSERT OR IGNORE` strategy combined with an `IntegrityError` catch handles duplicate email addresses, flashing an appropriate error message rather than crashing.

/login handles user authentication. On POST, it queries the `users` table by email, verifies the password hash using `check_password_hash`, and stores the `user_id` in the session on success.

/browse is the main catalog browsing hub. It constructs a dynamic SQL query starting from a base join across `comics`, `comic_status`, and `comic_type`, then conditionally appends WHERE clauses based on the user's filter selections: status, type, title search (using SQL `LIKE`), and tag-based filtering via a subquery on the `comic_tags` junction table. Sorting options include highest rating, alphabetical title, and most chapters. I chose to build the query dynamically with parameter binding rather than using an ORM because it gives precise control over the join structure and keeps the filtering logic transparent. The route also supports AJAX requests — if the `X-Requested-With` header is `XMLHttpRequest`, it returns only the comic grid partial template, enabling dynamic filtering without full page reloads.

/comic_details/<int:comic_id> renders a detailed view for a single comic using a complex SQL query that joins across seven tables: `comics`, `author_works`, `authors`, `comic_tags`, `tags`, `comic_status`, `comic_type`, and a LEFT JOIN on `reading_list` scoped to the current user. This single query retrieves the comic's metadata, its author, all associated tags, the user's personal reading status, their rating, their current chapter progress, and the community average rating calculated via a correlated subquery.

/add-comic provides a form for submitting new titles. On POST, it validates that all required fields are present (title, author, description, chapters, image URL, status, type, and at least one tag), checks for duplicate titles, resolves the foreign key IDs for status and type from their respective reference tables, and then executes a series of inserts across `comics`, `authors`, `author_works`, and `comic_tags`. The multi-table insertion is wrapped in separate try-except blocks to provide granular error feedback. I debated using a database transaction for atomicity but chose individual error handling for better user-facing error messages during development.

/add_reading_list/<int:comic_id> adds a comic to the current user's reading list with a default status of "Reading" (status ID 1). The `INSERT OR IGNORE` prevents duplicate entries without throwing errors.

/change_reading_status/<int:comic_id> updates the reading status for a specific comic in the user's reading list. It validates that a status ID was provided before executing the update.

/remove_reading_list/<int:comic_id> removes a comic from the user's reading list entirely, using a DELETE query scoped to both the comic ID and the authenticated user's ID.

/add-rating/<int:comic_id> allows users to rate a comic they have in their reading list. The rating is stored per-user in the `reading_list` table, and the community average is computed dynamically via a subquery in the detail view rather than being cached, ensuring it is always current.

/set-num-chapters/<int:comic_id> updates the user's current chapter progress for a specific comic. It includes validation to ensure the submitted chapter number does not exceed the comic's total chapter count, preventing invalid progress tracking.

/reading-list renders the user's personal reading list dashboard. The base query joins `reading_list`, `comics`, `comic_type`, and `reading_status`, and can be filtered by status category (Reading, Completed, Plan to Read) via POST. A second query calculates the count of comics in each status category using a LEFT JOIN to ensure all three categories appear even when empty, providing the tab counts for the dashboard interface.

### Database Schema

The database uses a normalized relational design with the following tables:
users — stores user accounts with hashed passwords
comics — the core comic catalog with title, description, chapter count, cover image, and foreign keys to type and status
authors — author names, linked to comics via the `author_works` junction table
author_works — many-to-many relationship between authors and comics
tags — genre tags
comic_tags — many-to-many relationship between comics and tags
comic_type — reference table for Manga, Manhwa, Manhua
comic_status — reference table for Ongoing, Completed, Hiatus
reading_status — reference table for Reading, Completed, Plan to Read
reading_list — per user tracking with reading status, current chapter, and personal rating

## Tech Stack

Framework - Flask (Python)
Database - SQLite3
Templating - Jinja2
Auth - Werkzeug password hashing
Sessions - Flask-Session (filesystem)
HTML/CSS (via templates)

## Getting Started

pip install flask flask-session werkzeug
python app.py
The development server starts at `http://localhost:5000`. The database is created and seeded automatically on first run.
