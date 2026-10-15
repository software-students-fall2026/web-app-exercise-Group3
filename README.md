# Web Application Exercise

A student assignment tracker web app built with Flask, MongoDB, HTML, and CSS.

## Product vision statement

A web app that helps students keep track of their assignments, deadlines, and progress in one place.

## User stories

User stories are tracked in the [GitHub Issues](https://github.com/software-students-fall2026/web-app-exercise-Group3/issues).

## Steps necessary to run the software

1. Clone the repository:

   ```bash
   git clone https://github.com/software-students-fall2026/web-app-exercise-Group3.git
   cd web-app-exercise-Group3
   ```

2. Run the repository setup script:

   ```bash
   python3 .automations/setup.py
   ```

3. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install the required packages:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Create the environment file:

   ```bash
   cp env.example .env
   ```

6. Start the Flask application:

   ```bash
   python app.py
   ```

7. Open `http://127.0.0.1:5000` in your browser.

The MongoDB database will run locally using Docker. Database setup instructions will be added once the team finishes configuring Docker.

## Task boards

[Group 3 - Sprint 1](https://github.com/orgs/software-students-fall2026/projects/37/views/1)

Sprint 2 board: To be added.