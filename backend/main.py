from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess, smtplib, os

app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class EmailRequest(BaseModel):
    email: str
    content: str

# Serve static frontend files
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Speed test (placeholder — currently uses curl to llsapi.com)
@app.get("/speedtest")
async def speedtest():
    results = []
    for _ in range(3):
        r = subprocess.run(["curl", "-s", "https://speedtest.llsapi.com"], capture_output=True, text=True)
        results.append(r.stdout.strip())
    return {"results": results}

# Send email with test results
@app.post("/send")
async def send_email(req: EmailRequest):
    sender = os.getenv("EMAIL_USER", "noreply@example.com")
    password = os.getenv("EMAIL_PASSWORD", "")
    to = req.email
    subject = "Test Results"
    msg = f"Subject: {subject}\n\n{req.content}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender, password)
            smtp.sendmail(sender, to, msg)
        return {"status": "sent"}
    except Exception as e:
        return {"error": str(e)}
