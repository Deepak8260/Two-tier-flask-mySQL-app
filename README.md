# FlaskBoard — Two-Tier Message Board

A production-ready **two-tier web application** built with **Python Flask** and **MySQL**.
Users post messages that are stored in MySQL and displayed in real time.

The app is designed to be run **locally**, **with Docker**, and **deployed on AWS EC2** — all
covered step-by-step in this README.

---

## Tech Stack

| Layer    | Technology                     |
|----------|--------------------------------|
| Frontend | HTML5 · CSS3 · Jinja2          |
| Backend  | Python 3 · Flask               |
| Database | MySQL 8                        |
| Runtime  | Docker (for cloud deployment)  |
| Cloud    | AWS EC2                        |

---

## Architecture

```
Browser  (HTML + CSS + JS)
    │
    │  GET  /              ← fetch & display all messages
    │  POST /add           ← submit a new message
    │  POST /delete/<id>   ← delete a message
    ▼
Flask Container  (app.py)
    │
    │  database.py handles all SQL queries
    ▼
MySQL Container  (messagesdb → messages table)
    id · message · created_at · ip_address
```

### Docker Network Diagram

```
┌─────────────────────────────────────────────┐
│            flask-mysql-net  (Docker network) │
│                                             │
│  ┌──────────────────┐  ┌─────────────────┐  │
│  │  flask-container │  │ mysql-container │  │
│  │  port 5000       │◄─►  port 3306      │  │
│  └──────────────────┘  └─────────────────┘  │
│           │                                 │
└───────────┼─────────────────────────────────┘
            │
     ← User Traffic (port 5000) →
```

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
├── app.py                 # Flask routes
├── database.py            # MySQL helpers
├── config.py              # Reads DB config from env vars
├── requirements.txt       # Python dependencies
├── .env.example           # Credentials template (copy → .env)
├── .gitignore             # Excludes venv, .env, __pycache__
└── README.md
```

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

> **Note:** The table is created automatically on first run — no manual SQL needed.

---

## Features

| Feature | Detail |
|---|---|
| Post messages | Saved to MySQL with timestamp + source IP |
| Live search | Filter the message log client-side (no reload) |
| Delete messages | Per-row delete with confirmation |
| Auto DB bootstrap | Database + table created on first startup |
| Env-based config | Credentials from `.env` — no hardcoded secrets |
| PRG pattern | No duplicate submissions on browser refresh |

---

---

# 🖥️ Option 1 — Run Locally (without Docker)

### Prerequisites
- Python 3.8+
- MySQL 8 running locally

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/Deepak8260/Two-tier-flask-mySQL-app.git
cd Two-tier-flask-mySQL-app

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux

# 5. Edit .env with your MySQL credentials
#    DB_HOST=localhost
#    DB_USER=root
#    DB_PASSWORD=your_password
#    DB_NAME=messagesdb

# 6. Run the app
python app.py
```

Visit **http://localhost:5000**

---

---

# 🐳 Option 2 — Run with Docker

Use this method to run both Flask and MySQL inside Docker containers on any machine.

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

---

### Step 1 — Create a Dockerfile for the Flask app

Create a file named `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

---

### Step 2 — Pull the official MySQL image from Docker Hub

```bash
docker pull mysql:8.0
```

---

### Step 3 — Create a Docker network

Both containers must be on the same network so they can communicate by container name.

```bash
docker network create flask-mysql-net
```

---

### Step 4 — Run the MySQL container

```bash
docker run -d \
  --name mysql-container \
  --network flask-mysql-net \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=messagesdb \
  -p 3306:3306 \
  mysql:8.0
```

> Wait ~15 seconds for MySQL to finish initialising before starting Flask.

Verify it's running:

```bash
docker ps
docker logs mysql-container
```

---

### Step 5 — Build the Flask Docker image

```bash
docker build -t flask-app .
```

---

### Step 6 — Run the Flask container

```bash
docker run -d \
  --name flask-container \
  --network flask-mysql-net \
  -e DB_HOST=mysql-container \
  -e DB_USER=root \
  -e DB_PASSWORD=password \
  -e DB_NAME=messagesdb \
  -p 5000:5000 \
  flask-app
```

> `DB_HOST=mysql-container` — Flask resolves this to the MySQL container's IP automatically via the Docker network.

---

### Step 7 — Open the app

```
http://localhost:5000
```

---

### Useful Docker commands

```bash
# View running containers
docker ps

# View Flask app logs
docker logs flask-container

# View MySQL logs
docker logs mysql-container

# Stop both containers
docker stop flask-container mysql-container

# Remove both containers
docker rm flask-container mysql-container

# Remove the network
docker network rm flask-mysql-net
```

---

---

# ☁️ Option 3 — Deploy on AWS EC2 (Recommended)

Deploy the full stack on an AWS EC2 instance using Docker.

---

### Step 1 — Launch an EC2 Instance

1. Go to **AWS Console → EC2 → Launch Instance**
2. Choose **Ubuntu Server 22.04 LTS (Free Tier eligible)**
3. Instance type: `t2.micro` (Free Tier)
4. **Key pair**: Create or select an existing `.pem` key
5. **Security Group** — Add these inbound rules:

| Type       | Protocol | Port | Source    |
|------------|----------|------|-----------|
| SSH        | TCP      | 22   | Your IP   |
| Custom TCP | TCP      | 5000 | 0.0.0.0/0 |

6. Launch the instance

---

### Step 2 — SSH into the EC2 instance

```bash
# Replace with your key file and EC2 public IP
ssh -i "your-key.pem" ubuntu@<EC2-PUBLIC-IP>
```

---

### Step 3 — Install Git and Docker on EC2

Install both tools manually **or** use the one-shot script below.

**Manual install:**

```bash
# Update & upgrade packages
sudo apt update -y
sudo apt upgrade -y

# Install Git
sudo apt install git -y

# Install Docker
sudo apt install docker.io -y

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Allow running Docker without sudo
sudo usermod -aG docker $USER

# Apply group change for the current session
newgrp docker

# Verify both tools
git --version
docker --version
```

**Or — run the one-shot setup script (faster):**

```bash
# Download and run the bootstrap script
curl -fsSL https://raw.githubusercontent.com/Deepak8260/Two-tier-flask-mySQL-app/main/setup.sh | bash
```

> The `setup.sh` script does all of the above automatically in one command.

---

### Step 4 — Clone the repository

```bash
git clone https://github.com/Deepak8260/Two-tier-flask-mySQL-app.git
cd Two-tier-flask-mySQL-app
```

---

### Step 5 — Pull the MySQL image from Docker Hub

```bash
docker pull mysql:8.0
```

---

### Step 6 — Create a Docker network

```bash
docker network create flask-mysql-net
```

---

### Step 7 — Run the MySQL container

```bash
docker run -d \
  --name mysql-container \
  --network flask-mysql-net \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=messagesdb \
  -p 3306:3306 \
  mysql:8.0
```

Wait ~15 seconds, then verify:

```bash
docker logs mysql-container
# Look for: "ready for connections"
```

---

### Step 8 — Create the Dockerfile on EC2

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY .  .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
EOF
```

---

### Step 9 — Build the Flask image on EC2

```bash
docker build -t flask-app .
```

---

### Step 10 — Run the Flask container

```bash
docker run -d \
  --name flask-container \
  --network flask-mysql-net \
  -e DB_HOST=mysql-container \
  -e DB_USER=root \
  -e DB_PASSWORD=password \
  -e DB_NAME=messagesdb \
  -p 5000:5000 \
  flask-app
```

---

### Step 11 — Access the application

```
http://<EC2-PUBLIC-IP>:5000
```

Find your EC2 public IP in **AWS Console → EC2 → Instances → Public IPv4 address**

---

### Verify everything is running on EC2

```bash
# Both containers should show STATUS = Up
docker ps

# Check Flask logs for any errors
docker logs flask-container

# Check MySQL logs
docker logs mysql-container
```

---

### Troubleshooting

| Problem | Fix |
|---|---|
| `Connection refused` on port 5000 | Check EC2 Security Group allows port 5000 inbound |
| Flask can't connect to MySQL | Wait 15–20s for MySQL to fully start, then restart Flask container |
| `docker: command not found` | Run `sudo apt-get install -y docker.io` again |
| Page not loading | Run `docker ps` — make sure both containers are `Up` |

---

## Roadmap

- [x] Local Flask + MySQL setup
- [x] Docker containerisation
- [x] AWS EC2 deployment
- [ ] Docker Compose (single command to start all services)
- [ ] Push images to Amazon ECR
- [ ] Deploy on AWS ECS / EKS
- [ ] CI/CD pipeline with GitHub Actions or Jenkins
- [ ] Kubernetes manifests + Helm chart
- [ ] HTTPS with Nginx reverse proxy
---

## License

MIT
