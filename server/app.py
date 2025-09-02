from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from models import db, User, Recipe

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecret"

db.init_app(app)
migrate = Migrate(app, db)


# ---------------------- SIGNUP ----------------------
@app.post("/signup")
def signup():
    data = request.get_json()

    try:
        new_user = User(
            username=data.get("username"),
            image_url=data.get("image_url"),
            bio=data.get("bio")
        )
        new_user.password_hash = data.get("password")
        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 422


# ---------------------- CHECK SESSION ----------------------
@app.get("/check_session")
def check_session():
    user_id = session.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user:
            return jsonify(user.to_dict()), 200
    return jsonify({"error": "Unauthorized"}), 401


# ---------------------- LOGIN ----------------------
@app.post("/login")
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get("username")).first()

    if user and user.authenticate(data.get("password")):
        session["user_id"] = user.id
        return jsonify(user.to_dict()), 200
    return jsonify({"error": "Unauthorized"}), 401


# ---------------------- LOGOUT ----------------------
@app.delete("/logout")
def logout():
    if session.get("user_id"):
        session.pop("user_id")
        return "", 204
    return jsonify({"error": "Unauthorized"}), 401


# ---------------------- RECIPE INDEX ----------------------
@app.get("/recipes")
def recipes_index():
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401

    recipes = Recipe.query.all()
    return jsonify([r.to_dict() for r in recipes]), 200


@app.post("/recipes")
def create_recipe():
    if not session.get("user_id"):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    try:
        new_recipe = Recipe(
            title=data.get("title"),
            instructions=data.get("instructions"),
            minutes_to_complete=data.get("minutes_to_complete"),
            user_id=session["user_id"]
        )
        db.session.add(new_recipe)
        db.session.commit()
        return jsonify(new_recipe.to_dict()), 201
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 422
