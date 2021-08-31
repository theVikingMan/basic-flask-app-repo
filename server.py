from werkzeug.serving import run_simple
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
import sqlalchemy
from sqlalchemy.engine import Engine
from flask import Flask, json, request, jsonify, redirect, url_for, render_template, session, flash
from datetime import datetime
from datetime import timedelta
from sqlite3 import Connection as SQLite3Connection



# Creating an instance of the class Flask

app = Flask(__name__)
app.debug = True
app.secret_key = "coffee"
app.permanent_session_lifetime = timedelta(hours=5)

# Configuring the flask app to connect to our database through SQL Alchemy
# Spelling matters for the all caps section
# Second configuration is so there arent other errors in the server start up

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///usersdb.file"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# configure sqlite3 to enforce foreign key contraints
# Imported sqlalchemy modules just for the code block below
# Below is pretty cookie cutter code to enfore FK constraint

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

# Creating an database object 
# Connecting our ORM to our flask application

db = SQLAlchemy(app)
now = datetime.now()



# Creating our schema for the data base "User" and the "Feedback" forms
# To create the database file: Enter into the python virtual environment
# >>> from server import db
# >>> db.create_all()
# >>> exit()



# Database table models
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))


# Routes for the API
@app.route('/Home')
def home():
    return render_template("index.html")


# Side additions for login, not part of the main project

@app.route("/view")
def view():
    return render_template("view.html", values=User.query.all())

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method =="POST":
        session.permanent = True
        user = request.form["user_login"]
        session["user"] = user

        found_user = User.query.filter_by(name=user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = User(name=user)
            db.session.add(usr)
            db.session.commit()

        flash("Login successful", "info")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in!", "info")
            return redirect(url_for("user"))
        return render_template("login.html")



@app.route("/user", methods=["POST", "GET", "DELETE"])
def user():
    email = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            if request.form["submit"] == "Submit Email":
                email = request.form["email"]
                session["email"] = email
                found_user = User.query.filter_by(name=user).first()
                found_user.email = email
                db.session.commit()
                flash("Email was saved!")
            if request.form["submit"] == "Delete Email":
                email = request.form["email"]
                session["email"] = email
                found_user = User.query.filter_by(name=user).first()
                found_user.email = None
                db.session.commit()
                flash("Email Deleted!")
        else:
            if "email" in session:
                email = session["email"]
        return render_template("user.html", name=user)
    else:
        flash("Not logged in!", "info")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f"{user} Successfuly logged out!", "info")
    session.pop("user", None)
    session.pop("name", None)
    return redirect(url_for("login"))

if __name__ == '__main__':
    db.create_all()
    run_simple('localhost', 5002, app,
               use_reloader=True, use_debugger=True, use_evalex=True)
