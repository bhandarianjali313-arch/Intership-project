@echo off
echo =====================================================================
echo    Deploying LexiGuard AI Platform inside Docker Containers
echo =====================================================================
echo.

docker compose up --build -d

echo.
echo =====================================================================
echo    Docker Containers Deployed Successfully!
echo    * Web Application:  http://localhost:5173
echo    * Backend REST API: http://localhost:8000
echo    * Swagger Docs:     http://localhost:8000/docs
echo =====================================================================
echo.
pause
