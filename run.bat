@echo off
echo Starting Referral ^& Rewards API...
call conda activate referral-backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
