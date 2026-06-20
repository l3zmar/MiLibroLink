import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from supabase import create_client, Client

from helpers import apology, login_required, lookup, usd, is_int
from database import insert_book

load_dotenv()

# Configure application
app = Flask(__name__, template_folder='templates', static_folder='static')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure Supabase database
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        try:
            response = supabase.table("Usuarios").select("*").eq("username", request.form.get("username")).execute()
            rows = response.data
        except Exception as e:
            return apology(f"Database error: {str(e)}", 500)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/main")

    else:
        return render_template("login.html")

@app.route("/main", methods=["GET", "POST"])
@login_required
def main():
    if request.method == "POST":
        book_id = request.form.get("book_id")
        user_id = session["user_id"]
        try:
            supabase.table("Usuarios").update({"current_book": book_id}).eq("id", user_id).execute()
        except Exception as e:
            return apology(f"Database error: {str(e)}", 500)
        return redirect("/main")
    else:
        user_id = session["user_id"]
        try:
            response = supabase.table("UserLibrary").select("*").eq("user_id", user_id).execute()
            rows = response.data

            current_book_response = supabase.table("Usuarios").select("current_book").eq("id", user_id).execute()
            current_book_query = current_book_response.data
        except Exception as e:
            return apology(f"Database error: {str(e)}", 500)

        if current_book_query:
            current_book = current_book_query[0]
        else:
            current_book = None

    return render_template("main.html", rows=rows, current_book=current_book)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        nombre = request.form.get("name")
        password = request.form.get("password")

        try:
            response = supabase.table("Usuarios").select("*").eq("username", nombre).execute()
            rows = response.data
        except Exception as e:
            return apology(f"Database error: {str(e)}", 500)

        if len(rows) == 1:
            return apology("username already exist", 400)
        else:
            hashcode = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            try:
                supabase.table("Usuarios").insert({"username": nombre, "password": hashcode}).execute()
            except Exception as e:
                return apology(f"Database error: {str(e)}", 500)
            return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/profile")
@login_required
def profile():
    user_id = session["user_id"]
    try:
        response = supabase.table("Usuarios").select("username").eq("id", user_id).execute()
        rows = response.data
    except Exception as e:
        return apology(f"Database error: {str(e)}", 500)
    return render_template("profile.html")

# Configura la clave de API de Google Books
GOOGLE_BOOKS_API_KEY = "AIzaSyAZ7X6jUncbjsNf8S4xgSICqVKgbYYcvPM"

@app.route("/search")
@login_required
def search():
    return render_template("search.html")

@app.route("/book", methods=["POST"])
def book():
    return ""

@app.route("/biblioteca")
@login_required
def biblioteca():

    user_id = session["user_id"]

    try:
        response = supabase.table("UserLibrary").select("*").eq("user_id", user_id).execute()
        rows = response.data
    except Exception as e:
        return apology(f"Database error: {str(e)}", 500)

    return render_template("biblioteca.html", rows = rows)

@app.route("/addBook", methods=["POST"])
@login_required
def addBook():
    title = request.form.get("title")
    authors = request.form.get("authors")
    thumbnail = request.form.get("thumbnail")
    user_id = session["user_id"]

    try:
        supabase.table("UserLibrary").insert({
            "title": title,
            "author": authors,
            "thumbnail": thumbnail,
            "user_id": user_id
        }).execute()
    except Exception as e:
        return apology(f"Database error: {str(e)}", 500)

    return redirect("/biblioteca")

if __name__ == "__main__":
    app.run(debug=True)
