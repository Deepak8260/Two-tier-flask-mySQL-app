# Two-Tier Flask App — Message Board

A **two-tier web application** built with Python Flask and MySQL. Users can post messages that are stored in a MySQL database and displayed in real time. The app is structured cleanly for future **containerisation with Docker** and **deployment on AWS**.

---

## Tech Stack

| Layer    | Technology              |
|----------|-------------------------|
| Frontend | HTML5 · CSS3 · Jinja2   |
| Backend  | Python 3 · Flask        |
| Database | MySQL 8                 |

---

## Project Structure

```
two-tier-flask-app/
│
├── templates/
│     └── index.html       # Jinja2 HTML template
│
├── static/
│     └── style.css        # Dark professional UI
│
├── app.py                 # Flask routes (GET / · POST /add · POST /delete/<id>)
├── database.py            # MySQL helpers (connect, init, insert, fetch, delete, stats)
├── config.py              # Reads DB credentials from environment variables
├── requirements.txt       # Python dependencies
├── .env.example           # Template — copy to .env and fill in your credentials
├── .gitignore             # Ignores venv, .env, __pycache__, IDE files
└── README.md
```

---

## Architecture

```
Browser  (HTML + CSS + JS)
    │
    │  GET  /              ← fetch & display all messages
    │  POST /add           ← submit a new message
    │  POST /delete/<id>   ← delete a message
    ▼
Flask App  (app.py)
    │
    │  database.py handles all SQL queries
    ▼
MySQL  (messagesdb → messages table)
    id · message · created_at · ip_address
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/two-tier-flask-app.git
cd two-tier-flask-app
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure credentials

```bash
# Copy the example env file
cp .env.example .env   # Windows: copy .env.example .env
```

Open `.env` and set your MySQL password:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_actual_password
DB_NAME=messagesdb
```

> The `.env` file is listed in `.gitignore` and will **never** be committed.

### 5. Run the application

```bash
python app.py
```

The server starts at **http://localhost:5000**

> On first run, `init_db()` automatically creates the `messagesdb` database and `messages` table if they don't already exist — no manual SQL required.

---

## Database Schema

```sql
CREATE TABLE messages (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    message    TEXT        NOT NULL,
    created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) DEFAULT NULL
);
```

---

## Features

| Feature | Detail |
|---|---|
| Post messages | Saved to MySQL with timestamp + source IP |
| Live search | Filter the message log client-side |
| Delete messages | Per-row delete with confirmation |
| Auto table creation | DB and table created on first run |
| Env-based config | Credentials read from `.env` — not hardcoded |
| PRG pattern | No duplicate submissions on browser refresh |

---

## Roadmap (Future / DevOps)

- [ ] Containerise with Docker (Flask + MySQL containers)
- [ ] Push images to Amazon ECR
- [ ] Deploy on AWS ECS / EKS
- [ ] CI/CD pipeline with GitHub Actions or Jenkins
- [ ] Kubernetes manifests + Helm chart

---

## License

MIT
