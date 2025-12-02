# Backend Project - User Management System

This project allows managing users and a data array using Python (FastAPI).
It uses a PostgreSQL database to save users and supports secure Login/Register processes.

## What does this project do?

* **Users:** You can register, login, and get a secure Token.
* **Admins:** Special users can "promote" or "demote" others.
* **Security:** Passwords are encrypted (hashed) so they are not saved as plain text.
* **Data:** Saves everything in a real PostgreSQL database.
* **Structure:** The code is organized in a "Layered" structure (Controllers, Services, Repositories) inside a `src` folder.

---

## Prerequisites (What you need)

* **Python 3.12+** installed.
* **Docker Desktop** (Recommended for easy running).
* **PostgreSQL** (Only if you want to run it manually without Docker).

---

## Step 1: Configuration (.env)

The project includes a smart setup that allows running both locally and via Docker without changing configuration files constantly.

1.  **Create the file:**
    Copy the file named `.env.example` and rename the copy to `.env`.

2.  **Default Setup:**
    Keep the default settings in `.env` pointing to **localhost**. This serves your local development (`uvicorn`).

    ```ini
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=node_exercise
    ```

    > **Note for Docker users:** You don't need to change `POSTGRES_HOST`. The `docker-compose.yml` file automatically overrides this to `db` when running inside containers.

---

## Option 1: Running with Docker (Recommended)

This installs the database and the server automatically inside containers.

### Start the Project
Run this command to build the project and start it in the background:
```bash
docker-compose up -d --build


Check if it's running
To see the logs and make sure everything is okay:
**docker-compose logs -f**
Stop the Project
To stop and remove the containers:
docker-compose down
### Option 2: Running Locally (Manual)
If you prefer to run the project on your own machine without Docker, follow these steps.

1. Database Setup
Make sure you have PostgreSQL installed and running.

Open pgAdmin (or SQL Shell) and create a new database named exactly: node_exercise.

Important: Open your .env file and make sure it points to your local computer:

POSTGRES_HOST=localhost
2. Python Environment
Open your terminal (PowerShell or CMD) inside the project folder and run these commands one by one:

Step A: Create a virtual environment

python -m venv .venv
Step B: Activate the environment

Windows:
.\.venv\Scripts\Activate.ps1
source .venv/bin/activate
Step C: Install libraries

pip install -r requirements.txt
3. Run the Server
Start the application using this command:

uvicorn src.main:app --reload
The API will be available at http://127.0.0.1:8000.

Code Structure
The code is inside the src folder:

controllers/: The "Managers". They receive the request and check if the Database is connected.
services/: The "Logic". Checks passwords, encrypts data, and applies rules.
repositories/: The "Warehouse". Talks directly to the database (SQLAlchemy).
routers/: The "Menu". Defines the URLs (like /login, /users).
models.py: Defines how the tables look in the database.

How to Test?
Open your browser at: http://localhost:8000/docs
Try the POST /users to create a new user.
Try the POST /auth/login to get a Token.
