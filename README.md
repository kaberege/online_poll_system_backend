# Online Poll System Backend

A Django REST Framework–based backend for managing polls, votes, and users with JWT authentication.  
This project allows users to create polls, vote, and manage their accounts securely.

---

## Features

- User authentication and authorization with **JWT** (`rest_framework_simplejwt`)
- Create, update, delete, and list **polls**
- Vote on polls (restricted to one vote per user per poll)
- Prevent voting on **expired polls**
- Swagger UI (`drf_yasg`) for API documentation
- PostgreSQL database support
- CORS enabled for frontend integration
- Static & media file handling with WhiteNoise

---

## Installation & Setup

### Clone the repository

```bash
git clone https://github.com/kaberege2/online_poll_system_backend.git
cd online_poll_system_backend
```

### Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Copy `.env.dist` → `.env` and update values:

```env
SECRET_KEY=your_secret_key
DATABASE_NAME=pollDB
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### Apply migrations

```bash
python manage.py migrate
```

### Create a superuser

```bash
python manage.py createsuperuser
```

### Run the server

```bash
python manage.py runserver
```

---

## API Documentation

After starting the server, visit:

- Swagger UI: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- ReDoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

---

## Authentication

This project uses **JWT (JSON Web Tokens)**.

- Obtain token:

  ```http
  POST /api/auth/login/
  ```

- Refresh token:

  ```http
  POST /api/auth/token/refresh/
  ```

- Use token in requests:

  ```
  Authorization: Bearer <your_token>
  ```

---

## Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (`djangorestframework-simplejwt`)
- **Documentation**: drf-yasg (Swagger & ReDoc)
- **Other Tools**: django-cors-headers, django-filter, whitenoise
