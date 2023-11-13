from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, status
from routes.jwt import create_access_token, get_user
from passlib.context import CryptContext
from db.connection import cursor, conn

from models.token import Token
from models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60

auth = APIRouter()

@auth.post("/login", response_model=Token)
async def login_for_access_token(username: str = Form(...), password: str = Form(...)):
    query = ("SELECT * FROM users WHERE username = %s")
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result and pwd_context.verify(password, result["password"]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return {"message": "Login successfully", "access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@auth.post("/register")
async def register(username: str = Form(...), password: str = Form(...), role: str = Form(default="user"), loc: int = Form(...)):
    query = ("SELECT * FROM users WHERE username = %s")
    cursor.execute(query, (username,))
    result = cursor.fetchall()
    if result:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Username already exist")
    
    query = ("SELECT * FROM locs WHERE id = %s")
    cursor.execute(query, (loc,))
    result = cursor.fetchall()
    if not result:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Location does not exist")
    
    
    hashed_password = pwd_context.hash(password)
    query = "INSERT INTO users (username, password, role, loc_id) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (username, hashed_password, role, loc,))
    conn.commit()
    return {
            "messages" : "Register successfully",
            "data" : {
                "username" : username,
            }
    }

@auth.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_user)]):
    return current_user