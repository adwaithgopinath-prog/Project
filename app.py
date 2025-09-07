from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# ------------------------
# Flask setup
# ------------------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
db = SQLAlchemy(app)

# ------------------------
# Database Model
# ------------------------
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    carbon = db.Column(db.Float, nullable=False)
    suggestion = db.Column(db.String(500))
    category = db.Column(db.String(50), default="Other")
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize DB
with app.app_context():
    db.create_all()

# ------------------------
# Rule-based Suggestions
# ------------------------
def rule_based_suggestion(task):
    task = task.lower()
    if "car" in task: return "Use public transport or carpool."
    if "flight" in task: return "Try a train or video call instead of flying."
    if "meat" in task: return "Choose plant-based meals."
    if "printing" in task: return "Use digital docs to save paper."
    if "server" in task: return "Use renewable energy data centers."
    return "Try an eco-friendly alternative."

# ------------------------
# Carbon Estimation
# ------------------------
def estimate_co2(task):
    task = task.lower()
    if "flight" in task: return 90.0, "Travel"
    if "car" in task: return 15.0, "Travel"
    if "train" in task: return 6.0, "Travel"
    if "bike" in task or "cycle" in task: return 0.5, "Travel"
    if "bus" in task: return 8.0, "Travel"
    if "meat" in task: return 20.0, "Food"
    if "chicken" in task: return 6.0, "Food"
    if "vegan" in task or "vegetable" in task: return 2.0, "Food"
    if "printing" in task or "paper" in task: return 3.0, "Office"
    if "server" in task or "cloud" in task: return 25.0, "Office"
    return 5.0, "Other"

# ------------------------
# Routes
# ------------------------
@app.route("/")
def index():
    tasks = Task.query.all()
    total = sum(t.carbon for t in tasks)
    budget = 100  

    # Categories summary
    categories = {}
    for t in tasks:
        categories[t.category] = categories.get(t.category, 0) + t.carbon

    # Simple daily and weekly placeholders
    daily = {"Mon": 12, "Tue": 8, "Wed": 10, "Thu": 14, "Fri": 7}
    weekly = {"Week 1": 40, "Week 2": 55, "Week 3": 38, "Week 4": 62}

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        budget=budget,
        categories=categories or {},
        daily=daily or {},
        weekly=weekly or {}
    )

@app.route("/add", methods=["POST"])
def add_task():
    name = request.form["name"]
    carbon_input = request.form.get("carbon")

    if carbon_input:
        carbon = float(carbon_input)
        category = "Custom"
    else:
        carbon, category = estimate_co2(name)

    suggestion = rule_based_suggestion(name)
    new_task = Task(name=name, carbon=carbon, category=category, suggestion=suggestion)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/done/<int:task_id>")
def mark_done(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = True
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/clear")
def clear_tasks():
    Task.query.delete()
    db.session.commit()
    return redirect(url_for("index"))

# ------------------------
# Run
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)