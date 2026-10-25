import os
import re

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, abort, session
from functools import wraps

# Load environment variables
load_dotenv()

# Create the Flask application
app = Flask(__name__)

# Secret key so Flask can keep admins logged in with sessions
app.secret_key = os.getenv("SECRET_KEY") or "dev-secret-key"

# MongoDB configuration
mongo_uri = os.environ["MONGO_URI"]
db_name = os.getenv("MONGO_DB_NAME", "campus_board")

# Connect to MongoDB
client = MongoClient(
    mongo_uri,
    serverSelectionTimeoutMS=3000
)

db = client[db_name]
collection = db["items"]

admins = db["admins"]

# Create the default admin account if it doesn't exist yet
def create_default_admin():
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    try:
        if admins.find_one({"username": username}) is None:
            admins.insert_one({"username": username, "password": password})
    except PyMongoError:
        print("Could not reach MongoDB to create the default admin. Is Docker running?")


create_default_admin()

# Let every template know whether an admin is logged in
@app.context_processor
def inject_admin():
    return {"is_admin": session.get("is_admin", False)}

# Send visitors to the login page if they aren't logged in as admin
def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view

# Admin login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("is_admin"):
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = admins.find_one({"username": username, "password": password})
        if admin is None:
            return render_template(
                "login.html",
                username=username,
                error="Incorrect username or password."
            )

        session["is_admin"] = True
        session["admin_username"] = username
        return redirect(url_for("home"))

    return render_template("login.html", username="")

# Log the admin out
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Homepage route
@app.route("/")
def home():
    items = list(collection.find({"returned": {"$ne": True}, "resolved": {"$ne": True}}).sort("date_reported", -1))
    if session.get("is_admin"):
        lost_count = sum(
            1 for item in items if item.get("status") == "lost"
        )

        found_count = sum(
            1 for item in items if item.get("status") == "found"
        )

        return render_template(
            "admin_dashboard.html",
            items=items,
            lost_count=lost_count,
            found_count=found_count
        )
    return render_template("index.html", items=items)

# History page - admin only
@app.route("/history")
@admin_required
def history():
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"returned": True},
                    {"resolved": True}
                ]
            }
        },
        {
            "$addFields": {
                "completed_at": {
                    "$ifNull": [
                        "$date_returned",
                        "$date_resolved"
                    ]
                }
            }
        },
        {
            "$sort": {
                "completed_at": -1,
                "_id": -1
            }
        }
    ]

    items = list(collection.aggregate(pipeline))

    return render_template("history.html", items=items)

# Add a new lost or found post
@app.route("/add", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        new_post = {
            "item_name": request.form.get("item_name", "").strip(),
            "description": request.form.get("description", "").strip(),
            "status": request.form.get("status", "").strip(),
            "location": request.form.get("location", "").strip(),
            "date_reported": request.form.get("date_reported", "").strip(),
            "contact_email": request.form.get("contact_email", "").strip(),
        }

        if "" in new_post.values() or new_post["status"] not in ("lost", "found"):
            return render_template(
                "add.html",
                item=new_post,
                error="Please fill in all fields."
            )

        new_post["returned"] = False
        collection.insert_one(new_post)
        return redirect(url_for("home"))

    return render_template("add.html", item={})


#Look up a single item, tolerating ids that aren't valid ObjectIds
def find_item(item_id):
    try:
        item = collection.find_one({"_id": ObjectId(item_id)})
        return item
    except InvalidId:
        return None

#Item detail route
@app.route("/item/<item_id>")
def item_detail(item_id):
    item = find_item(item_id)
    if item is None:
        abort(404)
    return render_template("item.html", item=item)

#Delete confirmationa and deletion
@app.route("/item/<item_id>/delete", methods=["GET", "POST"])
@admin_required
def item_delete(item_id):
    item = find_item(item_id)
    if item is None:
        abort(404)

    if request.method == "POST":
        result = collection.delete_one({"_id": item["_id"]})
        if result.deleted_count == 0:
            abort(404)
        return redirect(url_for("home"))

    return render_template("delete.html", item=item)

#Edit a post
@app.route("/item/<item_id>/edit", methods=["GET", "POST"])
@admin_required
def item_edit(item_id):
    item = find_item(item_id)
    if item is None:
        abort(404)

    if request.method == "POST":
        updated = {
            "item_name": request.form.get("item_name", "").strip(),
            "description": request.form.get("description", "").strip(),
            "status": request.form.get("status", "").strip(),
            "location": request.form.get("location", "").strip(),
            "date_reported": request.form.get("date_reported", "").strip(),
            "contact_email": request.form.get("contact_email", "").strip(),
        }

        if "" in updated.values():
            updated["_id"] = item["_id"]
            return render_template(
                "edit.html",
                item=updated,
                error="Please fill in all fields."
            )

        collection.update_one({"_id": item["_id"]}, {"$set": updated})
        return redirect(url_for("item_detail", item_id=item_id))

    return render_template("edit.html", item=item)


# Complete a lost or found case - admin only
@app.route("/item/<item_id>/resolve", methods=["POST"])
@admin_required
def item_resolve(item_id):
    item = find_item(item_id)

    if item is None:
        abort(404)

    if item.get("returned") or item.get("resolved"):
        return redirect(url_for("item_detail", item_id=item_id))

    now = datetime.now(timezone.utc)

    if item.get("status") == "found":
        update = {
            "$set": {
                "returned": True,
                "resolved": False,
                "date_returned": now
            },
            "$unset": {"date_resolved": ""}
        }

    elif item.get("status") == "lost":
        update = {
            "$set": {
                "resolved": True,
                "returned": False,
                "date_resolved": now
            },
            "$unset": {"date_returned": ""}
        }

    else:
        abort(400)

    collection.update_one({"_id": item["_id"]}, update)

    return redirect(url_for("item_detail", item_id=item_id))


#Search by item name and filter by lost/found
@app.route("/search")
def search():
    keyword = request.args.get("keyword", "").strip()
    status = request.args.get("status", "")

    query = {"returned": {"$ne": True}, "resolved": {"$ne": True}}
    if keyword:
        query["item_name"] = {"$regex": re.escape(keyword), "$options": "i"}
    if status in ("lost", "found"):
        query["status"] = status

    items = list(collection.find(query))
    return render_template(
        "search.html",
        items=items,
        keyword=keyword,
        status=status
    )

# Return a completed case to active status
@app.route("/item/<item_id>/unresolve", methods=["POST"])
@admin_required
def item_unresolve(item_id):
    item = find_item(item_id)

    if item is None:
        abort(404)

    if not (item.get("returned") or item.get("resolved")):
        abort(400)

    collection.update_one(
        {"_id": item["_id"]},
        {
            "$set": {
                "returned": False,
                "resolved": False
            },
            "$unset": {
                "date_returned": "",
                "date_resolved": ""
            }
        }
    )

    return redirect(url_for("item_detail", item_id=item_id))

#Missing posts and unknown URLs
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

# Start the development server
if __name__ == "__main__":
    app.run(debug=True)