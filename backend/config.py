import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
os.makedirs(DB_DIR, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "blood-finder-secret-key")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(DB_DIR, "blood_finder.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False