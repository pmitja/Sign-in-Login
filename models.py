import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DB_URL", "sqlite:///app.db"))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    session_token = db.Column(db.String)
