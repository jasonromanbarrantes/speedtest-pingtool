from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from ping3 import ping
import subprocess, smtplib, os
from time import sleep

app = FastAPI()

# CORS
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

class PingRequest(BaseModel):
    userType: str

# Serve static frontend
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Speed test placeholder (site blocks automation)
@app.get("/speedtest")
async def speedtest():
    results = []
    for _ in range(3):
        r = subprocess.run(["curl", "-s", "https://speedtest.llsapi.com"], capture_output=True, text=True)
        results.append(r.stdout.strip())
    return {"results": results}

# Ping test with 600 pings per IP
@app.post("/pingtest")
async def pingtest(req: PingRequest):
    try:
        ips = {
            "interpreter": ["216.20.237.2", "216.20.235.2"],
            "linc": ["216.20.237.3", "216.20.235.3"]
        }[req.userType]

        results = {}
        for ip in ips:
            latencies = []
            for _ in range(600):  # 600 pings
                latency = ping(ip, timeout=2)
                if latency is not None:
                    latencies.append(latency)
                sleep(1)
            if latencies:
                results[ip] = {
                    "min_ms": min(latencies) * 1000,
                    "max_ms": max(latencies) * 1000,
                    "avg_ms": sum(latencies) / len(latencies) * 1000,
                    "count": len(latencies)
                }
            else:
                results[ip] = {
                    "error": "No replies received",
                    "count": 0
                }

        return {"summary": results}

    except Exception as e:
        return {"error": f"Ping test failed: {str(e)}"}

# Send email
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
