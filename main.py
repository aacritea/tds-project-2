from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from solver.quiz_solver import solve_quiz

app = FastAPI()

STORED_EMAIL = "your_email_here"
STORED_SECRET = "your_secret_here"

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
