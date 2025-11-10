@echo off
echo ====================================
echo Pushing Backend to GitHub
echo ====================================
echo.

cd /d "%~dp0"

echo Initializing git...
git init

echo Adding all files...
git add .

echo Committing...
git commit -m "Initial meme bot backend with content generator mode"

echo Adding remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/slaze929/MemeBot-backend.git

echo Pushing to GitHub...
git branch -M main
git push -u origin main --force

echo.
echo ====================================
echo Done! Check Railway for deployment.
echo ====================================
pause
