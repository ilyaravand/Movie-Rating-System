# Movie Rating System

Backend service for managing movies and ratings, built with FastAPI, PostgreSQL, and Docker.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Database Seeding](#database-seeding)
- [Development](#development)
- [Docker Commands](#docker-commands)

## 🎯 Overview

Movie Rating System is a RESTful API service that allows users to:
- Browse and search movies with pagination and filtering
- View detailed movie information including director, genres, and ratings
- Add, update, and delete movies
- Rate movies (1-10 scale)
- View aggregated rating statistics

## ✨ Features

- **8 Complete RESTful APIs** for movie management
- **Layered Architecture** (Controller-Service-Repository)
- **Database Relationships**: One-to-Many and Many-to-Many
- **Pagination & Filtering** for movie lists
- **Data Validation** with Pydantic
- **Error Handling** with custom exceptions
- **Docker Support** for easy deployment
- **Database Seeding** with 1000 movies

## 🛠 Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Dependency Management**: Poetry
- **Containerization**: Docker & Docker Compose
- **Language**: Python 3.12

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)

To check if Docker is installed:

```bash
docker --version
docker compose version
```

If Docker is not installed, follow the official installation guide:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Movie-Rating-System
```

### Step 2: Start the Services

Run the following command to build and start all services:

```bash
docker compose up --build -d
```

This command will:
- Build the FastAPI application image
- Start PostgreSQL database
- Start the FastAPI application
- Create necessary volumes and networks

### Step 3: Run Database Migrations

After the services are up, run the database migrations:

```bash
docker compose exec app alembic upgrade head
```

### Step 4: (Optional) Seed the Database

To populate the database with sample data (1000 movies):

```bash
# First, copy CSV files to the database container
docker compose cp scripts/tmdb_5000_movies.csv db:/tmp/
docker compose cp scripts/tmdb_5000_credits.csv db:/tmp/

# Then run the seeding script
docker compose exec db psql -U app_user -d app_db -f /tmp/seeddb.sql

# Or if you have the CSV files locally, you can use:
docker compose exec -T db psql -U app_user -d app_db < scripts/seeddb.sql
```

**Note**: The seeding script requires CSV files. If they are not in the repository, you may need to download them separately.

### Step 5: Verify the Setup

Check if the API is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ok"}
```

Check database connection:

```bash
curl http://localhost:8000/health/db
```

Expected response:
```json
{"status":"ok","db":"session_created"}
```

### Step 6: Access the API

- **API Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

## 📁 Project Structure

```
Movie-Rating-System/
├── app/
│   ├── controller/          # API route handlers
│   │   ├── movies.py       # Movie endpoints
│   │   ├── health.py       # Health check endpoints
│   │   └── api_v1.py       # API router configuration
│   ├── services/            # Business logic layer
│   │   └── movies_service.py
│   ├── repositories/        # Data access layer
│   │   └── movies_repository.py
│   ├── models/             # SQLAlchemy models
│   │   ├── movie.py
│   │   ├── director.py
│   │   ├── genre.py
│   │   └── movie_rating.py
│   ├── schemas/            # Pydantic schemas
│   │   ├── movie.py
│   │   ├── director.py
│   │   ├── genre.py
│   │   └── rating.py
│   ├── db/                 # Database configuration
│   │   ├── session.py
│   │   └── base.py
│   ├── exceptions/         # Custom exceptions
│   │   └── api_exceptions.py
│   └── main.py             # FastAPI application entry point
├── alembic/                # Database migrations
│   └── versions/
├── scripts/                # Utility scripts
│   ├── seeddb.sql         # Database seeding script
│   └── seed_check.py      # Seeding verification script
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore          # Docker ignore file
├── pyproject.toml         # Poetry dependencies
└── README.md              # This file
```

## 📚 API Documentation

### Base URL

All API endpoints are prefixed with `/api/v1`

### Endpoints

#### 1. Get Movies List (with Pagination & Filtering)

```http
GET /api/v1/movies
```

**Query Parameters:**
- `page` (int, default: 1): Page number
- `page_size` (int, default: 10, max: 100): Items per page
- `title` (string, optional): Filter by title (partial match)
- `release_year` (int, optional): Filter by release year
- `genre` (string, optional): Filter by genre name (partial match)

**Example:**
```bash
curl "http://localhost:8000/api/v1/movies?page=1&page_size=5&genre=Drama"
```

#### 2. Get Movie Details

```http
GET /api/v1/movies/{movie_id}
```

**Example:**
```bash
curl http://localhost:8000/api/v1/movies/1
```

#### 3. Create Movie

```http
POST /api/v1/movies
```

**Request Body:**
```json
{
  "title": "The Godfather",
  "director_id": 3,
  "release_year": 1972,
  "cast": "Marlon Brando, Al Pacino",
  "genres": [1, 5]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/movies \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Godfather",
    "director_id": 3,
    "release_year": 1972,
    "cast": "Marlon Brando, Al Pacino",
    "genres": [1, 5]
  }'
```

#### 4. Update Movie

```http
PUT /api/v1/movies/{movie_id}
```

**Request Body:**
```json
{
  "title": "The Godfather (Remastered)",
  "release_year": 1972,
  "cast": "Marlon Brando, Al Pacino",
  "genres": [1, 5, 7]
}
```

#### 5. Delete Movie

```http
DELETE /api/v1/movies/{movie_id}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/v1/movies/1
```

#### 6. Create Rating

```http
POST /api/v1/movies/{movie_id}/ratings
```

**Request Body:**
```json
{
  "score": 8
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/movies/1/ratings \
  -H "Content-Type: application/json" \
  -d '{"score": 8}'
```

#### 7. Health Check

```http
GET /health
GET /health/db
```

### Response Format

**Success Response:**
```json
{
  "status": "success",
  "data": { ... }
}
```

**Error Response:**
```json
{
  "status": "failure",
  "error": {
    "code": 404,
    "message": "Movie not found"
  }
}
```

## 🌱 Database Seeding

The project includes a seeding script to populate the database with sample data.

### Prerequisites

- CSV files: `tmdb_5000_movies.csv` and `tmdb_5000_credits.csv` in the `scripts/` directory

### Seeding Steps

1. **Copy CSV files to database container:**
   ```bash
   docker compose cp scripts/tmdb_5000_movies.csv db:/tmp/
   docker compose cp scripts/tmdb_5000_credits.csv db:/tmp/
   ```

2. **Run the seeding script:**
   ```bash
   docker compose exec db psql -U app_user -d app_db -f /tmp/seeddb.sql
   ```

3. **Verify seeding:**
   ```bash
   docker compose exec app python scripts/seed_check.py
   ```

Expected output:
```
Seeding Successful!
   - Movies loaded: 1000
   - Directors loaded: 2576
   - Genres loaded: 20
   - Ratings loaded: 16000
```

## 💻 Development

### Running Migrations

```bash
# Check current migration
docker compose exec app alembic current

# Run migrations
docker compose exec app alembic upgrade head

# Create new migration
docker compose exec app alembic revision --autogenerate -m "description"
```

### Viewing Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs app
docker compose logs db

# Follow logs
docker compose logs -f app
```

### Accessing the Container

```bash
# Enter app container
docker compose exec -it app sh

# Enter database container
docker compose exec -it db psql -U app_user -d app_db
```

### Running Tests

```bash
docker compose exec app pytest
```

## 🐳 Docker Commands

### Basic Commands

```bash
# Start services (detached mode)
docker compose up -d

# Start services with build
docker compose up --build -d

# Stop services
docker compose down

# Stop and remove volumes (⚠️ deletes database data)
docker compose down -v

# View running services
docker compose ps

# View logs
docker compose logs -f
```

### Service Management

```bash
# Restart a specific service
docker compose restart app

# Stop a specific service
docker compose stop app

# Start a specific service
docker compose start app

# Rebuild a specific service
docker compose up --build -d app
```

### Database Operations

```bash
# Access PostgreSQL shell
docker compose exec db psql -U app_user -d app_db

# Backup database
docker compose exec db pg_dump -U app_user app_db > backup.sql

# Restore database
docker compose exec -T db psql -U app_user -d app_db < backup.sql
```

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables (set in `docker-compose.yml`):

- `DATABASE_URL`: PostgreSQL connection string
  - Format: `postgresql+psycopg://user:password@host:port/database`
  - Default: `postgresql+psycopg://app_user:app_pass@db:5432/app_db`

### Database Configuration

Database settings are configured in `docker-compose.yml`:

- **Database Name**: `app_db`
- **Username**: `app_user`
- **Password**: `app_pass`
- **Port**: `5432` (internal, not exposed)

### Application Port

The FastAPI application runs on port `8000` and is exposed on `localhost:8000`.

## 🐛 Troubleshooting

### Services won't start

1. Check if ports are already in use:
   ```bash
   lsof -i :8000
   lsof -i :5432
   ```

2. Check Docker logs:
   ```bash
   docker compose logs
   ```

### Database connection errors

1. Ensure database is healthy:
   ```bash
   docker compose ps
   ```

2. Check database logs:
   ```bash
   docker compose logs db
   ```

3. Verify environment variables:
   ```bash
   docker compose exec app env | grep DATABASE_URL
   ```

### Migration errors

1. Check current migration status:
   ```bash
   docker compose exec app alembic current
   ```

2. View migration history:
   ```bash
   docker compose exec app alembic history
   ```

### Build errors

1. Clean Docker cache:
   ```bash
   docker system prune -a
   ```

2. Rebuild without cache:
   ```bash
   docker compose build --no-cache
   ```

## 📝 Notes

- The database data persists in a Docker volume named `movie-rating-system_pgdata`
- To start fresh, use `docker compose down -v` (⚠️ this deletes all data)
- The application automatically connects to the database using the service name `db`
- All API endpoints follow RESTful conventions
- API documentation is available at `/docs` (Swagger UI)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Commit with descriptive messages
4. Push and create a Pull Request

## 📄 License

This project is part of a Software Engineering course at AUT.

---

**Happy Coding! 🎬**
