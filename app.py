import os
import re

from bson.objectid import ObjectId
from bson.errors import InvalidId
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv

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

# Homepage route
@app.route("/")
def home():
    items = list(collection.find())
    return render_template("index.html", items=items)


# ---------- Edit + search ----------
def get_post(post_id):
    """Find one post by its id. Returns None if the id is invalid or not found."""
    try:
        return collection.find_one({"_id": ObjectId(post_id)})
    except InvalidId:
        return None


# Edit a post
@app.route("/edit/<post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = get_post(post_id)
    if post is None:
        return "Post not found.", 404

    if request.method == "POST":
        updated = {
            "item_name": request.form.get("item_name", "").strip(),
            "description": request.form.get("description", "").strip(),
            "category": request.form.get("category", "").strip(),
            "location": request.form.get("location", "").strip(),
            "date": request.form.get("date", "").strip(),
            "contact": request.form.get("contact", "").strip(),
        }

        # all fields required
        if "" in updated.values():
            return render_template(
                "edit.html",
                post=updated,
                post_id=post_id,
                error="Please fill in all fields."
            )

        collection.update_one({"_id": post["_id"]}, {"$set": updated})
        return redirect(url_for("home"))

    return render_template("edit.html", post=post, post_id=post_id)


#mark a post as resolved
@app.route("/resolve/<post_id>", methods=["POST"])
def resolve_post(post_id):
    post = get_post(post_id)
    if post is None:
        return "Post not found.", 404

    collection.update_one({"_id": post["_id"]}, {"$set": {"resolved": True}})
    return redirect(url_for("home"))


#search by item name and filter by lost/found
@app.route("/search")
def search():
    keyword = request.args.get("keyword", "").strip()
    category = request.args.get("category", "")

    query = {}
    if keyword:
        query["item_name"] = {"$regex": re.escape(keyword), "$options": "i"}
    if category in ("lost", "found"):
        query["category"] = category

    items = list(collection.find(query))
    return render_template(
        "search.html",
        items=items,
        keyword=keyword,
        category=category
    )

# Start the development server
if __name__ == "__main__":
    app.run(debug=True)