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
    except Exception as e:
        print(f"DATABASE ERROR: {e}")
        return []
    finally:
        conn.close()


def init_db():
    """Initialize the database if does not exist"""
    if not os.path.exists("manga_query.db"):
        print("Creating database...")
        conn = get_db_connection()
        with open("schema.sql", "r") as f:
            conn.executescript(f.read())
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
        return redirect("/")
    else:
        return render_template("auth.html")
