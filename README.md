# Web Application Exercise

## Campus Lost & Found

A mobile-first campus lost-and-found web application built with Flask, MongoDB, HTML, and CSS.

Students can report lost or found items, search existing posts, and view item details. Administrators can manage posts, track returned or resolved items, and review the history of completed cases.

## Product vision statement

Our goal is to provide students with a simple and accessible platform to report and find lost items on campus.

Students can browse, search, and create lost-and-found posts, while administrators can manage reported items and track their status.

The application is designed with a mobile-first interface so students can conveniently access it from their phones.

## Team Members

- **Lefei Ke (Coco)** — [GitHub](https://github.com/Carbo32N)
- **Denise** — [GitHub](https://github.com/denisekos)
- **Veer** - [GitHub](https://github.com/sing1179)
- **Asritha** — [GitHub](https://github.com/scanfasri)

## User stories

User stories are tracked in the [GitHub Issues](https://github.com/software-students-fall2026/web-app-exercise-Group3/issues).

### Student Features

- View active lost-and-found posts.
- Search for items by name.
- Filter posts by Lost or Found status.
- View post details and contact information.
- Create new lost-and-found posts.
- Access the application through a mobile-friendly interface.

### Admin Features

- Log in and log out using an admin account.
- View the admin dashboard with active Lost and Found post counts.
- Edit and delete existing posts.
- Mark found items as Returned.
- Mark lost items as Resolved.
- Reactivate completed posts.
- View returned and resolved posts in the History tab, sorted by completion date.

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

Create a `.env` file using the example configuration:

```bash
cp env.example .env
```

Update `.env` with the following information:

```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=campus_board
SECRET_KEY=your-generated-secret-key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

Generate a random secret key using:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Replace `your-generated-secret-key` with the generated value.

The `.env` file is excluded from GitHub through `.gitignore` and should not be committed.

### 6. Start MongoDB with Docker

Make sure Docker Desktop is installed and running.

Start MongoDB:

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

If no posts are available, the application displays an empty-state message.

If port 5000 is already in use,  start Flask on another port:

```bash
flask --app app run --debug --port 5001
```

Then visit:

 http://127.0.0.1:5001.

### 8. Admin Login

Click **Admin Login** in the top-right corner of the application.

For local testing, the default credentials are:

```text
Username: admin
Password: admin123
```

The default admin account is created automatically when Flask starts and MongoDB is available.

To use different credentials, update `ADMIN_USERNAME` and `ADMIN_PASSWORD` in your `.env` file before the first run. 

Admin accounts are stored in the `admins` collection in MongoDB.

After logging in, administrators can access the Dashboard, History, and item management features.

Click **Log Out** to return to the student view.

### 9. Stop the application

Stop Flask by pressing `Ctrl + C` in the terminal.

To stop MongoDB:

```bash
docker compose down
```

Database data is preserved in the Docker volume.

## Task boards

[Group 3 - Sprint 1](https://github.com/orgs/software-students-fall2026/projects/37/views/1)

[Group 3 - Sprint 2](https://github.com/orgs/software-students-fall2026/projects/61/views/1)