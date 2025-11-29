import asyncio
from playwright.async_api import async_playwright

async def ensure_browsers():
    async with async_playwright() as p:
        # This downloads browsers if missing
        await p.chromium.launch(headless=True)

asyncio.run(ensure_browsers())

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from solver.quiz_solver import solve_quiz

app = FastAPI()

STORED_EMAIL = "23f3003343@ds.study.iitm.ac.in"
STORED_SECRET = "classifiedInfo11"

class QuizRequest(BaseModel):
    email: str
    secret: str
    url: str

@app.post("/solve")
async def solve(request: QuizRequest):
    if request.secret != STORED_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    try:
        answer = await solve_quiz(request)
        return answer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
