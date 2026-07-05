from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "CHOMELO v1 API ONLINE"}