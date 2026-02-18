@echo off
echo 🚀 Deploying Customer Analytics System
echo ======================================

:: Stop any running containers
docker-compose down

:: Build and start containers
docker-compose up --build -d

:: Wait for services to be ready
echo Waiting for services to start...
timeout /t 10

:: Show status
docker-compose ps

echo.
echo ✅ Deployment complete!
echo 📊 Backend API: http://localhost:8000
echo 📈 Dashboard: http://localhost:3000
echo 📚 API Docs: http://localhost:8000/api/docs
echo.
echo To see logs: docker-compose logs -f
echo To stop: docker-compose down