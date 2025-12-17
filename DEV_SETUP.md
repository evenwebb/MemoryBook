# Local Development Setup (Without Docker)

This guide will help you run MemoryBook locally for development without Docker.

## Prerequisites

1. **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download Node.js](https://nodejs.org/)
3. **PostgreSQL** - Install locally or use Docker just for PostgreSQL
4. **Redis** - Install locally or use Docker just for Redis
5. **Tesseract OCR** - Required for OCR functionality

### Installing Prerequisites

#### macOS (using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# Install Redis
brew install redis
brew services start redis

# Install Tesseract OCR
brew install tesseract
```

#### Linux (Ubuntu/Debian)
```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Install Redis
sudo apt-get install redis-server
sudo systemctl start redis-server

# Install Tesseract OCR
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

#### Windows
- PostgreSQL: Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Redis: Download from [redis.io](https://redis.io/download) or use WSL
- Tesseract: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Alternative: Docker for Database/Redis Only

If you prefer, you can run just PostgreSQL and Redis in Docker:

```bash
docker run -d --name memorybook-postgres \
  -e POSTGRES_USER=memorybook \
  -e POSTGRES_PASSWORD=memorybook \
  -e POSTGRES_DB=memorybook \
  -p 5432:5432 \
  postgres:15-alpine

docker run -d --name memorybook-redis \
  -p 6379:6379 \
  redis:7-alpine
```

## Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create database:**
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE memorybook;
CREATE USER memorybook WITH PASSWORD 'memorybook';
GRANT ALL PRIVILEGES ON DATABASE memorybook TO memorybook;
\q
```

5. **Create storage directories:**
```bash
mkdir -p ../storage/images ../storage/thumbnails
```

6. **Initialize database:**
```bash
python -m app.core.init_db
```

7. **Start the backend server:**
```bash
python run_dev.py
```

The backend will be available at http://localhost:8000
API docs at http://localhost:8000/docs

## Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Running Everything

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate
python run_dev.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

### Terminal 3 - Database/Redis (if using Docker)
```bash
# Only if you're using Docker for PostgreSQL/Redis
docker start memorybook-postgres memorybook-redis
```

## Access the Application

- **Frontend**: http://localhost:5173
- **Upload Page**: http://localhost:5173/upload
- **API Docs**: http://localhost:8000/docs
- **Backend API**: http://localhost:8000

## Configuration

### Backend Configuration
Edit `backend/.env.dev` to customize:
- Database connection
- Redis connection
- Storage paths
- CORS origins

### Frontend Configuration
Edit `frontend/.env.dev` to customize:
- API URL (default: http://localhost:8000/api/v1)

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `psql -U memorybook -d memorybook`
- Check Redis is running: `redis-cli ping`
- Verify Tesseract is installed: `tesseract --version`

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check CORS settings in `backend/app/core/config.py`
- Check `frontend/.env.dev` has correct API URL

### Database connection errors
- Verify PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
- Check database credentials in `backend/.env.dev`
- Ensure database exists: `psql -U postgres -l`

### Images not saving
- Check storage directories exist: `ls -la storage/`
- Verify write permissions: `chmod -R 755 storage/`

## Development Tips

- Backend auto-reloads on file changes (thanks to uvicorn --reload)
- Frontend hot-reloads automatically (Vite)
- Use `http://localhost:8000/docs` to test API endpoints
- Check logs in terminal for debugging

## Stopping Services

- Backend: `Ctrl+C` in backend terminal
- Frontend: `Ctrl+C` in frontend terminal
- PostgreSQL: `brew services stop postgresql@15` (macOS) or `sudo systemctl stop postgresql` (Linux)
- Redis: `brew services stop redis` (macOS) or `sudo systemctl stop redis` (Linux)
- Docker containers: `docker stop memorybook-postgres memorybook-redis`

