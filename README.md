# Online Poll System Backend

A robust **Django REST Framework (DRF)** backend for managing real-time polls, secure voting, and user accounts. This system is architected for scalability with PostgreSQL, secured with JWT, and fully containerized with Docker.

## Key Features

- **Secure Auth**: JWT-based authentication.
- **Poll Management**: Full CRUD capabilities for polls and choices.
- **Smart Voting**:
  - Strict "one user, one vote" enforcement.
  - Automatic prevention of voting on expired polls.

- **Documentation**: Interactive API docs via Swagger and ReDoc.
- **Production Ready**: Optimized with Multi-stage Docker builds, WhiteNoise for static files, and Gunicorn support.

---

## Tech Stack

| Component     | Technology                         |
| ------------- | ---------------------------------- |
| **Framework** | Django 5.2 & Django REST Framework |
| **Database**  | PostgreSQL                         |
| **Auth**      | SimpleJWT                          |
| **Docs**      | drf-yasg (Swagger/OpenAPI)         |
| **Container** | Docker & Docker Compose            |

---

## Getting Started

### Prerequisites

- Docker & Docker Compose **OR** Python 3.12+ and PostgreSQL.

### Quick Start (Docker)

The easiest way to get the system running is using Docker:

1. **Clone & Enter**:

```bash
git clone https://github.com/kaberege/online_poll_system_backend.git
cd online_poll_system_backend

```

2. **Environment Setup**: Create a `.env` file from the provided `.env.dist`.
3. **Spin Up**:

```bash
docker compose up --build

```

_The server will be available at `http://localhost:8000`._

### Manual Installation

1. **Create a virtual environment**:

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

```

2. **Install dependencies**: `pip install -r requirements.txt`.
3. **Configure environment variables**: Copy `.env.dist` → `.env` and update values:
4. **Database**: Ensure PostgreSQL is running and credentials match your `.env`.
5. **Init**:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

```

---

## API Documentation

Once the server is running, explore the API interactively:

- Swagger UI: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- ReDoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

### Core Endpoints

| Method | Endpoint                | Description                      |
| ------ | ----------------------- | -------------------------------- |
| `POST` | `/api/auth/login/`      | Obtain JWT Access/Refresh tokens |
| `GET`  | `/api/polls/`           | List all active polls            |
| `POST` | `/api/polls/{id}/vote/` | Submit a vote (Auth required)    |
| `GET`  | `/api/polls/{id}/`      | Get detailed poll results        |
