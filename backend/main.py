from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from ping3 import ping
import subprocess, smtplib, os
from time import sleep
from threading import Thread
import uuid

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

class PingRequest(BaseModel):
    userType: str

# Ping result memory store
ping_jobs = {}

# Serve static frontend files
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# Speed test (placeholder — for future upgrade)
@app.get("/speedtest")
async def speedtest():
    results = []
    for _ in range(3):
        r = subprocess.run(["curl", "-s", "https://speedtest.llsapi.com"], capture_output=True, text=True)
        results.append(r.stdout.strip())
    return {"results": results}

# Start 10-minute ping test
@app.post("/pingtest")
async def start_pingtest(req: PingRequest):
    test_id = str(uuid.uuid4())
    ping_jobs[test_id] = {"status": "running"}

    def run_test():
        try:
            ips = {
                "interpreter": ["216.20.237.2", "216.20.235.2"],
                "linc": ["216.20.237.3", "216.20.235.3"]
            }[req.userType]

            results = {}
            for ip in ips:
                latencies = []
                total_sent = 600
                total_received = 0

                for _ in range(total_sent):
                    latency = ping(ip, timeout=2)
                    if latency is not None:
                        latencies.append(latency)
                        total_received += 1
                    sleep(1)

                total_lost = total_sent - total_received
                loss_percent = (total_lost / total_sent) * 100

                if latencies:
                    results[ip] = {
                        "min_ms": min(latencies) * 1000,
                        "max_ms": max(latencies) * 1000,
                        "avg_ms": sum(latencies) / len(latencies) * 1000,
                        "count": total_received,
                        "packet_loss_count": total_lost,
                        "packet_loss_percent": round(loss_percent, 2)
                    }
                else:
                    results[ip] = {
                        "error": "No replies",
                        "count": 0,
                        "packet_loss_count": total_sent,
                        "packet_loss_percent": 100.0
                    }

            ping_jobs[test_id] = {
                "status": "complete",
                "summary": results
            }

        except Exception as e:
            ping_jobs[test_id] = {"status": "error", "message": str(e)}

    Thread(target=run_test).start()
    return {"test_id": test_id}

# Poll for ping result
@app.get("/ping-status/{test_id}")
async def check_ping_status(test_id: str):
    return ping_jobs.get(test_id, {"status": "not_found"})

# Email results
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
