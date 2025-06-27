# Speed & Ping Test Web Tool

## Features
- Run 3x speed tests using speedtest.llsapi.com
- Run 10-minute ping tests for Interpreter Connect or Linc users
- Send results via email

## Setup
1. Install requirements: `pip install -r requirements.txt`
2. Run server: `uvicorn backend.main:app --reload`
3. Open `frontend/index.html` in browser

## Deployment
Push to GitHub and link to Railway for automatic deploy
