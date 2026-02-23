import sqlite3
import os
from functools import wraps
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "073003-manga-key-030323"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def login_required(f):
    """Decorate routes to require login."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def get_db_connection():
    """Connect to the database"""
    conn = sqlite3.connect("manga_query.db")
    conn.row_factory = sqlite3.Row
    return conn


def db_execute(q, *args):
    """Execute database queries"""
    conn = get_db_connection()
    try:
        cursor = conn.execute(q, args)
        conn.commit()
        if q.strip().upper().startswith("SELECT"):
            return cursor.fetchall()
        return None
    finally:
        conn.close()


comic_reading_status_val = ["Reading", "Completed", "Plan to Read"]
comic_type_val = ["Manwha", "Manga", "Manhua"]
comic_status_val = ["Ongoing", "Completed", "Hiatus"]
comic_tags_val = [
    "Action",
    "Adventure",
    "Comedy",
    "Fantasy",
    "Sci-Fi",
    "Drama",
    "Romance",
    "Horror",
    "Mystery",
    "Psychological",
    "Shonen",
    "Shojo",
    "Seinen",
    "Josei",
    "Slice of Life",
    "Isekai",
    "Historical",
    "Post-Apocalyptic",
    "Supernatural",
    "Villainess",
]


def init_db():
    """Initialize the database if does not exist"""
    if not os.path.exists("manga_query.db"):
        print("Creating database...")
        conn = get_db_connection()
        with open("schema.sql", "r") as f:
            conn.executescript(f.read())

        for r in comic_reading_status_val:
            db_execute("INSERT INTO reading_status (reading_status_name) VALUES(?)", r)

        for t in comic_type_val:
            db_execute("INSERT INTO comic_type (type_name) VALUES (?)", t)

        for s in comic_status_val:
            db_execute("INSERT INTO comic_status (status_name) VALUES (?)", s)

        for tag in comic_tags_val:
            db_execute("INSERT INTO tags (tags_name) VALUES (?)", tag)

        conn.close()
        print("Database initialized!")


init_db()


@app.route("/")
def home():
    """Show the landing page"""
    session.clear()
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    """Register users"""
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        if not email or not password:
            flash("Email or Password is Missing", "error")
            return redirect("/register")

        try:
            db_execute(
                "INSERT OR IGNORE INTO users (email , password, username) VALUES(? , ? , ?)",
                email,
                password,
                username,
            )
            flash("Account successfully registered", "success")
            return redirect("/register")
        except sqlite3.IntegrityError:
            flash("Account already exists", "error")
            return redirect("/register")
    else:
        return render_template("auth.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    """Logs in user"""
    session.clear()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email or password is missing", "error")
            return redirect("/login")

        rows = db_execute("SELECT * FROM users WHERE email = ?", email)
        print("DEBUG ROWS:", rows, flush=True)

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            flash("Invalid email or password", "error")
            return redirect("/login")

        session["user_id"] = rows[0]["user_id"]
        return redirect("/browse")
    return render_template("auth.html")


@app.route("/add-comic", methods=["POST", "GET"])
@login_required
def add_comic():
    """Adds Comic to the database"""
    if request.method == "POST":
        image = request.form.get("image-url")
        title = request.form.get("title")
        author = request.form.get("author")
        description = request.form.get("description")
        selected_type = request.form.get("type")
        status = request.form.get("status")
        num_chapters = request.form.get("num_chapters")
        selected_tags = request.form.getlist("add-tag")

        status_id = None
        type_id = None

        if (
            not title
            or not description
            or not num_chapters
            or not image
            or not status
            or not selected_type
            or not author
            or not selected_tags
        ):
            flash("Missing Details, Please Complete the Needed Input")
            return redirect("/add-comic")

        try:
            existing_comic = db_execute(
                "SELECT comic_id FROM comics WHERE title = ?", title
            )

            if existing_comic:
                flash("Comic already exists", "error")
                return redirect("/add-comic")

            status_id = db_execute(
                "SELECT * FROM comic_status WHERE status_name = ?", status
            )
            type_id = db_execute(
                "SELECT * FROM comic_type WHERE type_name = ?", selected_type
            )

            if not status_id or not type_id:
                flash("Invalid Input, Please Try Again")
                return redirect("/add-comic")
            status_id = status_id[0]["comic_status_id"]
            type_id = type_id[0]["comic_type_id"]

        except Exception as e:
            print(f"Unexpected error: {e}")
            flash("An internal error occurred.")
            return redirect("/add-comic")

        try:
            db_execute(
                "INSERT OR IGNORE INTO comics (title, comic_description, num_of_chapters , cover_image, comic_type_id, comic_status_id) VALUES(?, ?, ?, ?, ?, ?)",
                title,
                description,
                num_chapters,
                image,
                type_id,
                status_id,
            )

            db_execute(
                "INSERT OR IGNORE INTO authors (name) VALUES (?)",
                author,
            )
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash("An internal error occurred.")
            return redirect("/add-comic")

        try:
            author_id = db_execute("SELECT * FROM authors WHERE name = ?", author)
            comic_id = db_execute("SELECT * FROM comics WHERE title = ?", title)

            if not author_id or not comic_id:
                flash("Author or Comic Not Found")
                return redirect("/add-comic")

            author_id = author_id[0]["author_id"]
            comic_id = comic_id[0]["comic_id"]

            db_execute(
                "INSERT OR IGNORE INTO author_works (author_id , comic_id) VALUES(? , ?)",
                author_id,
                comic_id,
            )
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash("An internal error occurred.")
            return redirect("/add-comic")

        try:
            for tag in selected_tags:
                comic_tags_id = db_execute(
                    "SELECT * FROM tags WHERE tags_name = ?", tag
                )

                if not comic_tags_id:
                    flash("Invalid Comic Tag")
                    return redirect("/add-comic")

                comic_tags_id = comic_tags_id[0]["tags_id"]
                db_execute(
                    "INSERT OR IGNORE INTO comic_tags (comic_id , tags_id) VALUES(? , ?)",
                    comic_id,
                    comic_tags_id,
                )
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash("An internal error occurred.")
            return redirect("/add-comic")

        return redirect("/add-comic")

    else:
        comic_type = db_execute("SELECT type_name FROM comic_type")
        comic_status = db_execute("SELECT status_name FROM comic_status")
        comic_tags = db_execute("SELECT tags_name FROM tags")
        return render_template(
            "add_comics.html",
            tags=comic_tags,
            comic_type=comic_type,
            comic_status=comic_status,
        )


@app.route("/browse", methods=["GET", "POST"])
@login_required
def browse():
    """Brose comics"""
    q = "SELECT * FROM comics INNER JOIN comic_status USING (comic_status_id) INNER JOIN comic_type USING (comic_type_id) WHERE 1 + 1 "
    params = []
    if request.method == "POST":
        status_filter = request.form.get("comic_status")
        type_filter = request.form.get("comic_type")
        title_filter = request.form.get("search-title")
        tags_filter = request.form.getlist("add-tag")
        comic_order = request.form.get("comic_order")

        if status_filter:
            q += " AND status_name = ?"
            params.append(status_filter)
        if type_filter:
            q += " AND type_name = ?"
            params.append(type_filter)
        if title_filter:
            q += " AND title LIKE ?"
            params.append(f"%{title_filter}%")
        if tags_filter:
            placeholder = ", ".join(["?"] * len(tags_filter))
            q += f" AND comic_id IN (SELECT comic_id FROM comic_tags JOIN tags USING (tags_id) WHERE tags_name IN ({placeholder}))"
            params.extend(tags_filter)
        if comic_order == "highest-rating":
            q += " ORDER BY ratings DESC"
        elif comic_order == "asc-title":
            q += " ORDER BY title ASC"
        elif comic_order == "most-chapters":
            q += " ORDER BY num_of_chapters DESC"

    try:
        comic_list = db_execute(q, *params)
        comic_status = db_execute("SELECT * FROM comic_status")
        comic_type = db_execute("SELECT * FROM comic_type")
        comic_tags = db_execute("SELECT * FROM tags")

    except Exception as e:
        print(f"Unexpected error: {e}")
        flash("An internal error occurred.")
        return redirect("/browse")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template("partials/comic-grid.html", comic_list=comic_list)

    return render_template(
        "browse.html",
        comic_list=comic_list,
        comic_status=comic_status,
        comic_type=comic_type,
        comic_tags=comic_tags,
    )


@app.route("/comic_details/<int:comic_id>")
@login_required
def comic_details(comic_id):
    """Get comic details"""
    user_id = session["user_id"]
    specific_comic_details = db_execute(
        """
        SELECT 
            c.comic_id, 
            c.title, 
            c.comic_description, 
            c.cover_image,
            c.num_of_chapters,
            a.name AS author_name,
            t.tags_name,
            cs.status_name,
            ct.type_name,
            rl.reading_list_id,
            COALESCE(rl.rating , 0) AS user_rating,
            rl.reading_status_id,
            rl.current_chapter,
            (SELECT ROUND(AVG(rating), 1) FROM reading_list WHERE comic_id = c.comic_id) AS avg_rating
        FROM comics AS c
        INNER JOIN author_works AS aw ON c.comic_id = aw.comic_id
        INNER JOIN authors AS a ON aw.author_id = a.author_id
        INNER JOIN comic_tags AS ctgs ON c.comic_id = ctgs.comic_id
        INNER JOIN tags AS t ON ctgs.tags_id = t.tags_id
        INNER JOIN comic_status AS cs ON c.comic_status_id = cs.comic_status_id
        INNER JOIN comic_type AS ct ON c.comic_type_id = ct.comic_type_id
        LEFT JOIN reading_list AS rl ON c.comic_id = rl.comic_id AND rl.user_id = ?
        WHERE c.comic_id = ?
        """,
        user_id,
        comic_id,
    )
    reading_status = db_execute("SELECT * FROM reading_status")

    if not specific_comic_details:
        flash("Invalid selected comic")
        return redirect(f"/comic_details/{comic_id}")

    if not reading_status:
        flash("Invalid status")
        return redirect(f"/comic_details/{comic_id}")

    return render_template(
        "comic_details.html", details=specific_comic_details, status=reading_status
    )


@app.route("/add_reading_list/<int:comic_id>", methods=["POST", "GET"])
@login_required
def add_reading_list(comic_id):
    """Add comic to reading list"""
    if request.method == "POST":
        user_id = session["user_id"]
        db_execute(
            "INSERT OR IGNORE INTO reading_list (comic_id , user_id, reading_status_id) VALUES(?,?,?)",
            comic_id,
            user_id,
            1,
        )
    return redirect(f"/comic_details/{comic_id}")


@app.route("/change_reading_status/<int:comic_id>", methods=["POST", "GET"])
@login_required
def change_reading_status(comic_id):
    """Change reading status"""
    if request.method == "POST":
        user_id = session["user_id"]
        status_id = request.form.get("reading_status_id")

        if not status_id:
            flash("Invalid value for status")
            return redirect(f"/comic_details/{comic_id}")

        try:
            db_execute(
                "UPDATE reading_list SET reading_status_id = ? WHERE comic_id = ? AND user_id = ?",
                status_id,
                comic_id,
                user_id,
            )
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash("An internal error occurred.")
    return redirect(f"/comic_details/{comic_id}")


@app.route("/remove_reading_list/<int:comic_id>", methods=["POST", "GET"])
@login_required
def remove_reading_list(comic_id):
    """Remove comic from reading list"""
    if request.method == "POST":
        user_id = session["user_id"]
        try:
            db_execute(
                "DELETE FROM reading_list WHERE comic_id = ? AND user_id = ?",
                comic_id,
                user_id,
            )
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash("An internal error occurred.")
    return redirect(f"/comic_details/{comic_id}")


@app.route("/add-rating/<int:comic_id>", methods=["GET", "POST"])
@login_required
def add_rating(comic_id):
    """Adds rating to comic"""
    if request.method == "POST":
        rating = request.form.get("rating")
        user_id = session["user_id"]

        if not rating:
            flash("Missing rating value")
            return redirect(f"/comic_details/{comic_id}")

        try:
            db_execute(
                "UPDATE reading_list SET rating = ? WHERE user_id = ? AND comic_id = ?",
                rating,
                user_id,
                comic_id,
            )
        except Exception as e:
            print(f"Unexpected error: {e}")
            flash("An internal error occurred.")
    return redirect(f"/comic_details/{comic_id}")


@app.route("/set-num-chapters/<int:comic_id>", methods=["POST"])
@login_required
def set_num_chapters(comic_id):
    """Sets the chapter read"""
    user_id = session["user_id"]
    if not user_id:
        flash("Missing user, please login")
        return redirect("/login")
    if not comic_id:
        flash("Comic not found")
        return redirect(f"/comic_details/{comic_id}")

    max_chapter = db_execute(
        "SELECT CAST(num_of_chapters AS INTEGER) AS num_of_chapters FROM comics WHERE comic_id = ?",
        comic_id,
    )
    current_chapter = request.form.get("current-chapter")

    if max_chapter[0]["num_of_chapters"] < int(current_chapter):
        flash("Invalid Input")
        return redirect(f"/comic_details/{comic_id}")

    if not current_chapter:
        flash("Input missing, try again")
        return redirect(f"/comic_details/{comic_id}")

    try:
        db_execute(
            "UPDATE reading_list SET current_chapter = ? WHERE comic_id = ? AND user_id = ?",
            current_chapter,
            comic_id,
            user_id,
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        flash("An internal error occurred.")
    return redirect(f"/comic_details/{comic_id}")


@app.route("/reading-list")
@login_required
def reading_list():
    """Gets user's reading list"""
    user_id = session["user_id"]
    comic_list = db_execute(
        """
            SELECT 
                c.title,
                c.num_of_chapters,
                c.cover_image,
                rl.current_chapter,
                ct.type_name,
                rs.reading_status_name,
                (SELECT ROUND(AVG(rating), 1) FROM reading_list WHERE comic_id = c.comic_id) AS avg_rating
            FROM reading_list AS rl
            INNER JOIN comics AS c USING (comic_id)
            INNER JOIN comic_type AS ct ON c.comic_type_id = ct.comic_type_id
            INNER JOIN reading_status AS rs USING (reading_status_id)
            WHERE user_id = ?
        """,
        user_id,
    )

    total = db_execute(
        """
        SELECT 
            rs.reading_status_name,
            COUNT(rl.reading_status_id) AS total
        FROM reading_status AS rs
        LEFT JOIN reading_list AS rl
        USING(reading_status_id)
        GROUP BY rl.reading_status_id
        """
    )
    return render_template("reading_list.html", reading_list=comic_list, total=total)
