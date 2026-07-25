import os
from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///reply_tracker.db")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


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
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

    # Validating the given parameter
    # Username
        if not username:
            return apology("Not a valid Username", 400)
    # Password
        if not password:
            return apology("Not a valid Password", 400)
        if not confirmation:
            return apology("Couldn't confirm your input", 400)
        if password != confirmation:
            return apology("Passwords do not match", 400)

        # Hashing the password
        password = generate_password_hash(password)

        # Inserting new user
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, password)
        except ValueError:
            return apology("Already registered!", 400)
        return render_template("login.html")

        # Showing the Registration Form
    else:
        return render_template("register.html")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add a new contact"""
    if request.method == "POST":
        name = request.form.get("name")

        # Validating the name
        if not name:
            return apology("Not a valid Name", 400)

        # Inserting new contact
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO contacts (user_id, name, last_direction, last_timestamp) VALUES (?, ?, ?, ?)", session["user_id"], name, "from_me", timestamp)
        return redirect("/")

    else:
        return render_template("add.html")

def time_since_last_contact(last_timestamp):
    last_time = datetime.strptime(last_timestamp, "%Y-%m-%d %H:%M:%S")
    hours_since = (datetime.now() - last_time).total_seconds() / 3600
    return hours_since

@app.route("/", methods=["GET"])
@login_required
def index():
    """Show dashboard of contacts"""
    contacts = db.execute("SELECT * FROM contacts WHERE user_id = ?", session["user_id"])

    dashboard = []

    for contact in contacts:
        hours_since = time_since_last_contact(contact["last_timestamp"])
        overdue = contact["last_direction"] == "from_them" and hours_since >= 24
        dashboard.append({
            "id": contact["id"],
            "name": contact["name"],
            "hours_since": round(hours_since),
            "overdue": overdue
        })

    dashboard.sort(key=lambda x: x["hours_since"], reverse=True)
    return render_template("index.html", dashboard=dashboard)

@app.route("/update/<int:contact_id>", methods=["POST"])
@login_required
def update(contact_id):
    """Update contact's last interaction"""
    direction = request.form.get("direction")
    if direction not in ["from_me", "from_them"]:
        return apology("Invalid direction", 400)

    if direction == "from_me":
        # Nur bei "I replied" wird der Timer zurückgesetzt
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.execute(
            "UPDATE contacts SET last_direction = ?, last_timestamp = ? WHERE id = ? AND user_id = ?",
            direction, timestamp, contact_id, session["user_id"]
        )
        flash("You replied!")
    else:
        # Bei "They messaged me" nur die Richtung ändern, Timestamp bleibt
        db.execute(
            "UPDATE contacts SET last_direction = ? WHERE id = ? AND user_id = ?",
            direction, contact_id, session["user_id"]
        )
        flash("They messaged you!")

    return redirect("/")

@app.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    """Delete the logged-in user's account and all their contacts"""
    db.execute("DELETE FROM contacts WHERE user_id = ?", session["user_id"])
    db.execute("DELETE FROM users WHERE id = ?", session["user_id"])
    session.clear()
    return redirect("/login")

@app.route("/delete_contact/<int:contact_id>", methods=["POST"])
@login_required
def delete_contact(contact_id):
    """Delete a single contact"""
    db.execute("DELETE FROM contacts WHERE id = ? AND user_id = ?", contact_id, session["user_id"])
    flash("Contact deleted!")
    return redirect("/")
