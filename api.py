from fastapi import FastAPI
import psutil
import socket

app = FastAPI()

def get_ip():
    return socket.gethostbyname(socket.gethostname())

@app.get("/")
def home():
    return {"status": "online"}

@app.get("/status")
def status():
    return {
        "ip": get_ip(),
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }