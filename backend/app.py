import os
from functools import wraps

from flask import Flask, jsonify, request, render_template, session
from config import Config
from models import db, Donor
from seed import seed_data

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "templates"))
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "static"))

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)

app.config.from_object(Config)
app.secret_key = os.environ.get("SECRET_KEY", "blood-finder-secret-key")

db.init_app(app)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


with app.app_context():
    db.create_all()
    seed_data()


def clean_text(value, default=""):
    if value is None:
        return default
    return str(value).strip()


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({
                "success": False,
                "message": "Admin login required"
            }), 401
        return func(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "success": True,
        "message": "Blood Finder API is running"
    })


# --------------------------
# Admin Auth Routes
# --------------------------
@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = clean_text(data.get("username"))
    password = clean_text(data.get("password"))

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return jsonify({
            "success": True,
            "message": "Admin login successful"
        })

    return jsonify({
        "success": False,
        "message": "Invalid admin credentials"
    }), 401


@app.route("/api/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("is_admin", None)
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


@app.route("/api/admin/check", methods=["GET"])
def admin_check():
    return jsonify({
        "success": True,
        "is_admin": bool(session.get("is_admin"))
    })


# --------------------------
# Donor API Routes
# --------------------------
@app.route("/api/donors", methods=["GET"])
def get_donors():
    search = clean_text(request.args.get("search")).lower()
    blood_group = clean_text(request.args.get("blood_group"))
    city = clean_text(request.args.get("city"))
    available = clean_text(request.args.get("available")).lower()
    sort_by = clean_text(request.args.get("sort_by"), "newest")

    query = Donor.query

    if blood_group:
        query = query.filter(Donor.blood_group == blood_group)

    if city:
        query = query.filter(Donor.city.ilike(f"%{city}%"))

    if available in ["true", "false"]:
        query = query.filter(Donor.available == (available == "true"))

    donors = query.all()

    if search:
        filtered_donors = []
        for donor in donors:
            if (
                search in clean_text(donor.full_name).lower()
                or search in clean_text(donor.city).lower()
                or search in clean_text(donor.area).lower()
                or search in clean_text(donor.blood_group).lower()
            ):
                filtered_donors.append(donor)
        donors = filtered_donors

    if sort_by == "name_asc":
        donors.sort(key=lambda d: clean_text(d.full_name).lower())
    elif sort_by == "name_desc":
        donors.sort(key=lambda d: clean_text(d.full_name).lower(), reverse=True)
    elif sort_by == "city_asc":
        donors.sort(key=lambda d: clean_text(d.city).lower())
    elif sort_by == "available_first":
        donors.sort(key=lambda d: (not bool(d.available), clean_text(d.full_name).lower()))
    else:
        donors.sort(key=lambda d: d.created_at if d.created_at else 0, reverse=True)

    return jsonify({
        "success": True,
        "count": len(donors),
        "donors": [donor.to_dict() for donor in donors]
    })


@app.route("/api/donors/<int:donor_id>", methods=["GET"])
def get_single_donor(donor_id):
    donor = Donor.query.get_or_404(donor_id)
    return jsonify({
        "success": True,
        "donor": donor.to_dict()
    })


@app.route("/api/donors", methods=["POST"])
def add_donor():
    data = request.get_json(silent=True) or {}

    required_fields = ["full_name", "blood_group", "city", "phone", "email", "age"]
    for field in required_fields:
        if not clean_text(data.get(field)):
            return jsonify({
                "success": False,
                "message": f"{field} is required"
            }), 400

    try:
        age = int(data.get("age"))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "age must be a valid number"
        }), 400

    donor = Donor(
        full_name=clean_text(data.get("full_name")),
        blood_group=clean_text(data.get("blood_group")),
        city=clean_text(data.get("city")),
        area=clean_text(data.get("area")),
        phone=clean_text(data.get("phone")),
        email=clean_text(data.get("email")),
        age=age,
        gender=clean_text(data.get("gender")),
        available=bool(data.get("available", True)),
        last_donated=clean_text(data.get("last_donated"))
    )

    db.session.add(donor)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Donor registered successfully",
        "donor": donor.to_dict()
    }), 201


@app.route("/api/donors/<int:donor_id>", methods=["PUT"])
@admin_required
def update_donor(donor_id):
    donor = Donor.query.get_or_404(donor_id)
    data = request.get_json(silent=True) or {}

    try:
        donor.full_name = clean_text(data.get("full_name", donor.full_name))
        donor.blood_group = clean_text(data.get("blood_group", donor.blood_group))
        donor.city = clean_text(data.get("city", donor.city))
        donor.area = clean_text(data.get("area", donor.area))
        donor.phone = clean_text(data.get("phone", donor.phone))
        donor.email = clean_text(data.get("email", donor.email))
        donor.age = int(data.get("age", donor.age))
        donor.gender = clean_text(data.get("gender", donor.gender))
        donor.available = bool(data.get("available", donor.available))
        donor.last_donated = clean_text(data.get("last_donated", donor.last_donated))

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Donor updated successfully",
            "donor": donor.to_dict()
        })
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid donor data"
        }), 400


@app.route("/api/donors/<int:donor_id>", methods=["DELETE"])
@admin_required
def delete_donor(donor_id):
    donor = Donor.query.get_or_404(donor_id)
    db.session.delete(donor)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Donor deleted successfully"
    })


@app.route("/api/meta/cities", methods=["GET"])
def get_cities():
    cities = db.session.query(Donor.city).distinct().all()
    city_list = sorted([city[0] for city in cities if city[0]])
    return jsonify({
        "success": True,
        "cities": city_list
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)