import sqlite3
import os
from flask import Flask, redirect, render_template, request, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "073003-manga-key-030323"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


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
    return render_template("index.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    """Register users"""
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        if not email or not password:
            flash("Email or Password is Missing", "error")
            return redirect("/register")

        try:
            db_execute(
                "INSERT INTO users (email , password, username) VALUES(? , ? , ?)",
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
        return redirect("/add-comic")
    else:
        return render_template("auth.html")


@app.route("/add-comic", methods=["POST", "GET"])
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
                "INSERT INTO comics (title, comic_description, num_of_chapters , cover_image, comic_type_id, comic_status_id) VALUES(?, ?, ?, ?, ?, ?)",
                title,
                description,
                num_chapters,
                image,
                type_id,
                status_id,
            )

            db_execute(
                "INSERT INTO authors (name) VALUES (?) ON CONFLICT(name) DO NOTHING",
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
                "INSERT INTO author_works (author_id , comic_id) VALUES(? , ?)",
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
                    "INSERT INTO comic_tags (comic_id , tags_id) VALUES(? , ?)",
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


@app.route("/get_comics")
def get_comics():
    try:
        comic_list = db_execute("GET * FROM comics")
    except Exception as e:
        print(f"Unexpected error: {e}")
        flash("An internal error occurred.")
        return redirect("/get_comics")
