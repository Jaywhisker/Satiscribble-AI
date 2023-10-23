from fastapi import FastAPI
from fastapi import HTTPException

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
