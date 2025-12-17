#!/bin/bash
# Quick start script for local development

set -e

echo "🚀 Starting MemoryBook Development Environment"
echo ""

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 -U memorybook > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL is not running or not accessible"
    echo "   Please start PostgreSQL first:"
    echo "   macOS: brew services start postgresql@15"
    echo "   Linux: sudo systemctl start postgresql"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️  Redis is not running"
    echo "   Please start Redis first:"
    echo "   macOS: brew services start redis"
    echo "   Linux: sudo systemctl start redis"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start backend
echo "📦 Starting backend..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "Starting backend server on http://localhost:8000"
python run_dev.py &
BACKEND_PID=$!

cd ..

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting frontend server on http://localhost:8088"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ Development servers started!"
echo ""
echo "📱 Frontend: http://localhost:8088"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait

