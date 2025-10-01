from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cctms.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ----------------------------
# Database Model
# ----------------------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default="other")
    carbon = db.Column(db.Float, default=0.0)
    suggestion = db.Column(db.String(300), default="Consider a greener alternative")
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ----------------------------
# Helper Functions
# ----------------------------
def generate_suggestion(category):
    tips = {
        "travel": ["Try carpooling 🚗", "Use public transport 🚌", "Walk or cycle 🚴"],
        "food": ["Choose plant-based meals 🥦", "Avoid food waste ♻️", "Buy local produce 🥕"],
        "office": ["Switch off unused devices 💡", "Go paperless 📄", "Optimize AC/heating 🌡️"],
        "other": ["Recycle more ♻️", "Be mindful of consumption 🌍", "Support eco-friendly products 🌱"]
    }
    return random.choice(tips.get(category, ["Think sustainable! 🌿"]))


def calculate_daily():
    data = {}
    today = datetime.utcnow().date()
    for i in range(7):  # last 7 days
        day = today - timedelta(days=i)
        total = db.session.query(db.func.sum(Task.carbon))\
            .filter(Task.created_at >= datetime.combine(day, datetime.min.time()))\
            .filter(Task.created_at <= datetime.combine(day, datetime.max.time()))\
            .scalar() or 0
        data[day.strftime("%a")] = total
    return dict(reversed(data.items()))


def calculate_weekly():
    data = {}
    today = datetime.utcnow().date()
    for i in range(4):  # last 4 weeks
        start = today - timedelta(days=today.weekday() + i * 7)
        end = start + timedelta(days=6)
        total = db.session.query(db.func.sum(Task.carbon))\
            .filter(Task.created_at >= datetime.combine(start, datetime.min.time()))\
            .filter(Task.created_at <= datetime.combine(end, datetime.max.time()))\
            .scalar() or 0
        data[f"Week-{i+1}"] = total
    return dict(reversed(data.items()))


def calculate_categories():
    categories = ["travel", "food", "office", "other"]
    data = {}
    for c in categories:
        total = db.session.query(db.func.sum(Task.carbon))\
            .filter(Task.category == c).scalar() or 0
        data[c.capitalize()] = total
    return data


# ----------------------------
# Routes
# ----------------------------
@app.route("/", methods=["GET"])
def index():
    filter_category = request.args.get("category", "all")
    search_query = request.args.get("search", "")

    query = Task.query
    if filter_category != "all":
        query = query.filter_by(category=filter_category)
    if search_query:
        query = query.filter(Task.name.ilike(f"%{search_query}%"))

    tasks = query.order_by(Task.created_at.desc()).all()

    total = sum(t.carbon for t in tasks)
    budget = 100  # demo budget

    daily = calculate_daily()
    weekly = calculate_weekly()
    categories = calculate_categories()

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        budget=budget,
        filter_category=filter_category,
        search_query=search_query,
        daily=daily,
        weekly=weekly,
        categories=categories,
        daily_json=json.dumps(daily),
        weekly_json=json.dumps(weekly),
        categories_json=json.dumps(categories)
    )


@app.route("/add", methods=["POST"])
def add_task():
    name = request.form["name"]
    category = request.form.get("category", "other")
    carbon = request.form.get("carbon")

    try:
        carbon_value = float(carbon) if carbon else random.uniform(1, 5)
    except ValueError:
        carbon_value = 0.0

    suggestion = generate_suggestion(category)
    task = Task(name=name, category=category, carbon=carbon_value, suggestion=suggestion)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/done/<int:task_id>")
def mark_done(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/clear")
def clear_tasks():
    Task.query.delete()
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").lower()
    reply = "🌍 Try reducing your carbon footprint!"

    if "travel" in user_message:
        reply = generate_suggestion("travel")
    elif "food" in user_message:
        reply = generate_suggestion("food")
    elif "office" in user_message:
        reply = generate_suggestion("office")
    else:
        reply = generate_suggestion("other")

    return jsonify({"reply": reply})


# ----------------------------
# Init DB
# ----------------------------
@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("✅ Database initialized")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
