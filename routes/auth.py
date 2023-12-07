from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, status
from routes.jwt import check_is_admin, check_is_login, create_access_token, get_user
from passlib.context import CryptContext
from db.connection import connectDB
import requests

from models.token import Token
from models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 60

auth = APIRouter()

@auth.post("/login", response_model=Token)
async def login_for_access_token(username: str = Form(...), password: str = Form(...)):
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    query = ("SELECT * FROM users WHERE username = %s")
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result and pwd_context.verify(password, result["password"]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        friend_service_url = "https://resto-hemat-api.ambitiousmoss-bd081c95.australiaeast.azurecontainerapps.io/login/single"

        friend_token_data = {
            "username": username,
            "password": password
        }

        try:
            response = requests.post(friend_service_url, data=friend_token_data)
            response.raise_for_status()
            friend_response_data = response.json()
            friend_token = friend_response_data.get("access_token")
        except requests.RequestException as e:
            print(response.text)
            raise HTTPException(status_code=500, detail=f"Failed to generate token in friend's service: {str(e)}")
        
        query = "UPDATE users SET friend_token = %s WHERE username = %s"
        cursor.execute(query, (friend_token, username))
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Login successfully", "access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@auth.post("/login/single", response_model=Token)
async def login_friend(username: str = Form(...), password: str = Form(...)):
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    query = ("SELECT * FROM users WHERE username = %s")
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result and pwd_context.verify(password, result["password"]):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return {"message": "Login successfully", "access_token": access_token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@auth.post("/register")
async def register(username: str = Form(...), password: str = Form(...), role: str = Form(default="user"), lat: float = Form(...), lon: float = Form(...), flag: bool = Form(...)):
    query = ("SELECT * FROM users WHERE username = %s")
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (username,))
    result = cursor.fetchall()
    if result:
        raise HTTPException(status_code=status.HTTP_302_FOUND, detail="Username already exist")
    query = "INSERT INTO locs (latitude, longitude) VALUES (%s, %s)"
    cursor.execute(query, (lat,lon))

    select_query = "SELECT * FROM locs WHERE id = LAST_INSERT_ID();"
    cursor.execute(select_query)
    new_loc = cursor.fetchone()
       
    hashed_password = pwd_context.hash(password)
    query = "INSERT INTO users (username, password, role, loc_id) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (username, hashed_password, role, new_loc['id'],))
    conn.commit()

    cursor.close()
    conn.close()

    if flag : 
        friend_service_url = "https://resto-hemat-api.ambitiousmoss-bd081c95.australiaeast.azurecontainerapps.io/register"

        friend_data = {
            "username": username,
            "password": password,
            "email" : username,
            "full_name" : username,
            "flag" : False,
            "lat" : lat,
            "lon" : lon,
        }

        try :
            response = requests.post(friend_service_url, data=friend_data)
            response.raise_for_status()
        except requests.RequestException as e:
            print(response.text)
            raise HTTPException(status_code=500, detail=f"Failed to generate token in friend's service: {str(e)}")
    
    return {
            "messages" : "Register successfully",
            "data" : {
                "username" : username,
            }
    }

@auth.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_user)]):
    return current_user

@auth.get("/users/all")
async def read_users_all(admin: Annotated[bool, Depends(check_is_admin)]):
    if not admin :
        return {
            "messages" : "You are not allowed to use this service"
        }
    query = ("SELECT * FROM users")
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query,)
    result = cursor.fetchall()
    return {
        "data" : result
    }
    
@auth.get("/users/food")
async def read_users_all(check: Annotated[bool, Depends(check_is_login)]):
    if not check :
        return {
            "messages" : "You are not authenticated"
        }
    query = ("SELECT * FROM users WHERE role = %s")
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query,("food",))
    result = cursor.fetchall()
    return {
        "data" : result
    }