import os

from flask import Flask, render_template, request, redirect, url_for, abort
from pymongo import MongoClient
from dotenv import load_dotenv
from bson.objectid import ObjectId
from bson.errors import InvalidId

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

# Add a new lost or found item
@app.route("/add", methods=["GET", "POST"])
def add_post():
    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "").strip()
        location = request.form.get("location", "").strip()
        date_reported = request.form.get("date_reported", "").strip()
        contact_email = request.form.get("contact_email", "").strip()

        # Make sure all fields are filled out
        if (not item_name or not description or
            status not in ["lost", "found"] or
            not location or not date_reported or
            not contact_email):
            return render_template(
                "add.html",
                error="Please fill out all fields."
            ), 400

        # Create the new post
        new_post = {
            "item_name": item_name,
            "description": description,
            "status": status,
            "location": location,
            "date_reported": date_reported,
            "contact_email": contact_email
        }

        # Save to MongoDB
        collection.insert_one(new_post)

        # Return to homepage
        return redirect(url_for("home"))

    return render_template("add.html")

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

#Missing posts and unknown URLs
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404

# Start the development server
if __name__ == "__main__":
    app.run(debug=True)
