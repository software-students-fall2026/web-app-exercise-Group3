import os
import re

from flask import Flask, render_template, request, redirect, url_for, abort
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

# Load environment variables
load_dotenv()

# Create the Flask application
app = Flask(__name__)

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

###Temporary admin switch until login is ready####
@app.context_processor
def inject_admin():
    return {"is_admin": os.getenv("ADMIN_MODE") == "1"}


# Homepage route
@app.route("/")
def home():
    items = list(collection.find({"returned": {"$ne": True}, "resolved": {"$ne": True}}).sort("date_reported", -1))
    if os.getenv("ADMIN_MODE") == "1":
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
def history():
    if os.getenv("ADMIN_MODE") != "1":
        abort(403)

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
def item_resolve(item_id):
    if os.getenv("ADMIN_MODE") != "1":
        abort(403)

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
def item_unresolve(item_id):
    if os.getenv("ADMIN_MODE") != "1":
        abort(403)

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