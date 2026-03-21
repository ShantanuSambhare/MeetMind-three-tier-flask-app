# MeetMind — Two-Tier Flask App on AWS EC2 with Docker

A full-stack corporate productivity web application built as a **DevOps project** to demonstrate containerization, multi-container orchestration, and cloud deployment.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend + Backend | Python · Flask |
| Database | MySQL 5.7 |
| Containerization | Docker |
| Orchestration | Docker Compose |
| Cloud Server | AWS EC2 (Ubuntu 22.04) |
| CI/CD | Jenkins (optional) |

---

## Architecture

```
User (Browser)
     │
     │  HTTP :5000
     ▼
┌─────────────────────────────────────────┐
│           AWS EC2 Instance              │
│  ┌──────────────────────────────────┐   │
│  │       Docker Network: twotier    │   │
│  │                                  │   │
│  │  ┌─────────────┐  ┌───────────┐ │   │
│  │  │  Container 1│  │Container 2│ │   │
│  │  │  Flask App  │◄─►│  MySQL   │ │   │
│  │  │  Port: 5000 │  │Port: 3306 │ │   │
│  │  └─────────────┘  └───────────┘ │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

---

## Project Structure

```
Two-Tier-Flask/
├── app.py                  # Flask application & API routes
├── Dockerfile              # Single-stage Docker build
├── Dockerfile-multistage   # Optimized multi-stage Docker build
├── docker-compose.yml      # Multi-container orchestration
├── requirements.txt        # Python dependencies
├── Jenkinsfile             # CI/CD pipeline (Jenkins)
├── Makefile                # Build automation shortcuts
├── message.sql             # DB init SQL script
├── templates/
│   └── index.html          # Frontend web page
└── README.md
```

---

## Prerequisites

Make sure you have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Git

---

## Quick Start

### Option 1 — Docker Compose (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/ShantanuSambhare/Two-Tier-Flask.git
cd Two-Tier-Flask

# 2. Start both containers
docker compose up -d --build

# 3. Open in browser
http://localhost:5000
```

### Option 2 — Manual Docker Commands

```bash
# Step 1 — Build the Flask image
docker build -t meetmind-app .

# Step 2 — Create Docker network
docker network create twotier

# Step 3 — Run MySQL container
docker run -d \
  --name mysql \
  --network twotier \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=devops \
  -v mysql-data:/var/lib/mysql \
  mysql:5.7

# Step 4 — Run Flask container
docker run -d \
  --name meetmind \
  --network twotier \
  -p 5000:5000 \
  -e MYSQL_HOST=mysql \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=root \
  -e MYSQL_DB=devops \
  meetmind-app
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MYSQL_HOST` | MySQL container hostname | `mysql` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | `root` |
| `MYSQL_DB` | Database name | `devops` |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the web page |
| POST | `/add_employee` | Add a team member to DB |
| GET | `/get_employees` | Fetch all employees from DB |
| DELETE | `/delete_employee/<id>` | Delete an employee by ID |
| POST | `/add_meeting` | Save a meeting to DB |
| GET | `/get_meetings` | Fetch all saved meetings |

---

## AWS EC2 Deployment

```bash
# SSH into your EC2 instance
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

# Install Docker
sudo apt-get update -y
sudo apt-get install docker.io -y
sudo systemctl start docker
sudo usermod -aG docker ubuntu
newgrp docker

# Clone and run
git clone https://github.com/ShantanuSambhare/Two-Tier-Flask.git
cd Two-Tier-Flask
docker compose up -d --build

# Access the app
http://YOUR_EC2_PUBLIC_IP:5000
```

> Make sure port **5000** is open in your EC2 Security Group inbound rules.

---

## Multi-Stage Docker Build (Optimized)

Use `Dockerfile-multistage` for a smaller production image:

```bash
docker build -f Dockerfile-multistage -t meetmind-app:optimized .
```

---

## Makefile Shortcuts

```bash
make build   # Build Docker images
make run     # Start containers in background
make stop    # Stop all containers
make clean   # Stop, remove containers and prune system
```

---

## Stopping the App

```bash
# Docker Compose
docker compose down

# Manual
docker stop meetmind mysql
docker rm meetmind mysql
```

---

## Built By

**Shantanu Sambhare** — DevOps Student

- GitHub: [ShantanuSambhare](https://github.com/ShantanuSambhare)
- LinkedIn: [linkedin.com/in/shantanu-sambhare](https://linkedin.com/in/shantanu-sambhare)

---

