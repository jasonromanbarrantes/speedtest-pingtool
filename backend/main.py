from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess, asyncio, smtplib

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class EmailRequest(BaseModel):
    email: str
    content: str

class PingRequest(BaseModel):
    userType: str

@app.get("/speedtest")
async def speedtest():
    results = []
    for _ in range(3):
        r = subprocess.run(["curl", "-s", "https://speedtest.llsapi.com"], capture_output=True, text=True)
        results.append(r.stdout.strip())
    return {"results": results}

@app.post("/pingtest")
async def pingtest(req: PingRequest):
    ips = {
        "interpreter": ["216.20.237.2", "216.20.235.2"],
        "linc": ["216.20.237.3", "216.20.235.3"]
    }[req.userType]

    async def ping(ip):
        proc = await asyncio.create_subprocess_exec("ping", "-c", "600", ip, stdout=subprocess.PIPE)
        out, _ = await proc.communicate()
        return out.decode()

    tasks = [ping(ip) for ip in ips]
    result = await asyncio.gather(*tasks)
    return {"ping_results": dict(zip(ips, result))}

@app.post("/send")
async def send_email(req: EmailRequest):
    sender = "noreply@example.com"
    to = req.email
    subject = "Test Results"
    msg = f"Subject: {subject}\n\n{req.content}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login("your_email@gmail.com", "your_app_password")
            smtp.sendmail(sender, to, msg)
        return {"status": "sent"}
    except Exception as e:
        return {"error": str(e)}
