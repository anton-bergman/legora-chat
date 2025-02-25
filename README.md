# Legora Chat

This project is a simple real-time messaging application.

## Tech Stack

- **Frontend**:
  - React.js (TypeScript)
  - Axios (for API requests)
  - React Router (for page navigation)
  - WebSockets (for real-time messaging)

- **Backend**:
  - Flask (Python)
  - SQLAlchemy (ORM for database interaction)
  - JWT (for authentication)
  - WebSockets (for real-time communication)
  - PostgreSQL (for database storage)

## Project Setup

### Backend Setup (Flask)

1. Navigate to the backend directory:

```bash
cd legora-chat/backend
```


2. Create a virtual environment and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

### Database Setup (PostgreSQL)

Before proceeding with the database setup, make sure that you have PostgreSQL installed and the `psql` CLI tool available on your system.

1. Navigate to the backend directory and run the following command:

```bash
./setup_db.sh && ./seed_db.sh
```

- The `setup_db.sh` script will setup the database and perform initial migrations.

- The `seed_db.sh` script will populate the database with sample data.

### Frontend Setup (React)

1. Navigate to the frontend directory:

```bash
cd legora-chat/frontend
```

2. Install the dependencies:

```bash
npm install
```

## Run the App
Once the setup is complete, you can run the app with the following commands:

1. **Backend**:

Navigate to the backend directory and run the Flask app:

```bash
python app.py
```

The backend will be available at `http://127.0.0.1:5000`.

2. **Frontend**:

Navigate to the frontend directory and run the React app:

```bash
npm run dev
```
The frontend will be available at `http://localhost:5173`.


## Database Setup: Mock Users

The following mock users are created when you run the `seed_db.sh` script:

- User 1:

    - Username: anton
    - Password: password123

- User 2:

    - Username: bugge
    - Password: password123

- User 3:

    - Username: bergman
    - Password: password123

- User 4:

    - Username: alice
    - Password: password123

- User 5:

    - Username: bob
    - Password: password123

- User 6:

    - Username: charlie
    - Password: password123

You can log in with these credentials to test the app.
