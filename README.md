# Web Application Exercise

A campus lost-and-found board web app built with Flask, MongoDB, HTML, and CSS.

## Product vision statement

A web app that helps students report lost or found items on campus and find items they are looking for.

## User stories

User stories are tracked in the [GitHub Issues](https://github.com/software-students-fall2026/web-app-exercise-Group3/issues).

## Student and admin views

**Students** can browse active posts, search by item name, filter by lost or found, view post details, and add new posts.

**Admins** log in to access the admin dashboard, edit and delete posts, mark items as returned or resolved, view the History tab, and reactivate completed items.

## Steps necessary to run the software

### 1. Clone the repository

```bash
git clone https://github.com/software-students-fall2026/web-app-exercise-Group3.git
cd web-app-exercise-Group3
```

### 2. Run the repository setup script

```bash
python3 .automations/setup.py
```

### 3. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install the required packages

```bash
python -m pip install -r requirements.txt
```

### 5. Create the environment file

```bash
cp env.example .env
```

The default configuration is:

```text
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=campus_board
SECRET_KEY=change-me
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

`SECRET_KEY` is used by Flask to keep admins logged in. Replace `change-me` with any long random string, for example the output of:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Start MongoDB with Docker

Make sure Docker Desktop is installed and running.

```bash
docker compose up -d
```

Verify that MongoDB is running:

```bash
docker compose ps
```

### 7. Start the Flask application

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

The homepage retrieves and displays records from MongoDB.

If the collection is empty, the page displays "No posts available yet."

On macOS, if port 5000 is already in use (often by AirPlay Receiver), run the app on another port instead:

```bash
flask --app app run --debug --port 5001
```

Then open http://127.0.0.1:5001.

### 8. Log in as an admin

Click **Admin Login** in the navigation bar, or go to `/login`.

A default admin account is created automatically the first time the app starts while MongoDB is running:

```text
Username: admin
Password: admin123
```

To use different credentials, change `ADMIN_USERNAME` and `ADMIN_PASSWORD` in your `.env` file before the first run. Admin accounts are stored in the `admins` collection in MongoDB.

Once logged in, the navigation bar shows the Dashboard and History tabs. Click **Log Out** to return to the student view.

### 9. Stop the application

Stop Flask by pressing `Ctrl + C` in the terminal where it is running.

To stop MongoDB:

```bash
docker compose down
```

The database data is preserved in the Docker volume.

## Task boards

[Group 3 - Sprint 1](https://github.com/orgs/software-students-fall2026/projects/37/views/1)

Sprint 2 board: To be added.