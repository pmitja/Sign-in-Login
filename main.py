from flask import Flask, request, render_template, redirect, url_for, make_response
import hashlib, uuid
from models import db, User

app = Flask(__name__)
db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    user = db.query(User).filter_by(email=email).first()

    if not user:
        user = User(name=name, email=email, password=hashed_password)
        db.add(user)
        db.commit()

    if hashed_password != user.password:
        return redirect(url_for("index.html"))

    session_token = str(uuid.uuid4())
    user.session_token = session_token
    db.add(user)
    db.commit()

    response = make_response(redirect(url_for("profile")))
    response.set_cookie("session_token", session_token)
    return response


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        user.session_token = None
        db.add(user)
        db.commit()

    response = make_response(redirect(url_for("index")))
    response.set_cookie("session_token", "")
    return response


@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if user:
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for("index.html"))


@app.route("/profile/edit", methods=["GET", "POST"])
def edit():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:  # if user is found
            return render_template("edit.html", user=user)
        else:
            return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        new_password = request.form.get("new_password")

        if name:
            user.name = name
        if email:
            user.email = email
        if password == user.password:
            if new_password:
                new_hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                user.password = new_hashed_password
        else:
            return render_template("error.html", user=user)
        db.add(user)
        db.commit()

        return redirect(url_for("profile"))


@app.route("/profile/delete", methods=["GET", "POST"])
def delete():
    session_token = request.cookies.get("session_token")

    user = db.query(User).filter_by(session_token=session_token).first()

    if not user:
        return redirect(url_for("index"))

    if request.method == "POST":
        db.delete(user)
        db.commit()

        response = make_response(redirect(url_for("index")))
        response.set_cookie("session_token", "")
        return response
    return render_template("delete.html", user=user)