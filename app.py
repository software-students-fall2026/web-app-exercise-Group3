from flask import Flask, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create the Flask application
app = Flask(__name__)

# Homepage route
@app.route("/")
def home():
    return render_template("index.html")

# Start the development server
if __name__ == "__main__":
    app.run(debug=True)
