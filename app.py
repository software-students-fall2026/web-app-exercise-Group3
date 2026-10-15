import os

from flask import Flask, render_template
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

# Start the development server
if __name__ == "__main__":
    app.run(debug=True)
