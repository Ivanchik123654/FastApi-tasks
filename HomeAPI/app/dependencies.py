import os
from dotenv import load_dotenv
from pathlib import Path
from fastapi import Header, HTTPException, status, Request

BASE_DIR = Path(__file__).resolve().parent.parent

print((BASE_DIR/'.env').exists())
print(BASE_DIR)

load_dotenv(BASE_DIR/'.env')
S_TOKEN = os.getenv("STUDENT_TOKEN")
T_TOKEN = os.getenv("TEACHER_TOKEN")
A_TOKEN = os.getenv("ADMIN_TOKEN")

print(S_TOKEN, T_TOKEN, A_TOKEN)

def verify_token(request: Request, api_token: str | None = Header(default=None)) -> None:
    print(api_token)
    if request.method == "GET":
        if api_token not in [S_TOKEN, A_TOKEN]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")
    elif request.method == "POST" or request.method == "DELETE":
        if api_token not in [T_TOKEN, A_TOKEN]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")
    elif request.method == "PATCH":
        if api_token != A_TOKEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")
    else:
        if api_token != A_TOKEN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")