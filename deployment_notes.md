# Render.com Deployment Requirements

## Configuration for FastAPI on Render

**Language**: Python 3

**Build Command**: `pip install -r requirements.txt`

**Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Steps
1. Create repository on GitHub (already done: jakelevi88hp/ApexOrchestrator)
2. Create new Web Service on Render
3. Connect GitHub repository
4. Provide configuration values above
5. Deploy

## Notes
- Free tier available
- Automatic SSL certificates
- Auto-deploys from Git
- URL format: `*.onrender.com`

