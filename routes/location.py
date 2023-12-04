from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from routes.jwt import check_is_admin, check_is_login, get_user
from models.location import Loc
from models.user import User
from db.connection import connectDB

loc = APIRouter()

@loc.get('/loc')
async def read_data(user: Annotated[User, Depends(get_user)]):
    if user['role'] == 'admin':
          query = "SELECT * FROM locs;"
          conn = connectDB()
          cursor = conn.cursor(dictionary=True)
          cursor.execute(query)
          data = cursor.fetchall()
          cursor.close()
          conn.close()
          return {
			"messages" : "Get All Location successfully",
			"data" : data
        }
    else:
        query = "SELECT * FROM locs where id = %s"
        conn = connectDB()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (user['loc_id'],))
        cursor.close()
        conn.close()
        data = cursor.fetchall()
        return {
			"messages" : "Get Your Location successfully",
			"data" : data
        }

@loc.get('/loc/{id}')
async def read_data(id: int, check: Annotated[bool, Depends(check_is_login)]):
    if not check:
        return
    select_query = "SELECT * FROM locs WHERE id = %s;"
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_query, (id,))
    cursor.close()
    conn.close()
    data = cursor.fetchone()

    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data Loc id {id} Not Found")
    
    return {
        "messages" : "Get Location successfully",
        "data" : data
    }

@loc.post('/loc')
async def write_data(loc: Loc, check: Annotated[bool, Depends(check_is_login)]):
    if not check:
        return
    loc_json = loc.model_dump()

    query = "INSERT INTO locs (latitude, longitude) VALUES(%s, %s);"
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, (loc_json["latitude"], loc_json["longitude"],))
    conn.commit()

    select_query = "SELECT * FROM locs WHERE id = LAST_INSERT_ID();"
    cursor.execute(select_query)
    new_loc = cursor.fetchone()
    cursor.close()
    conn.close()


    return {
        "messages" : "Add loc successfully",
        "data" : new_loc
    }
    
@loc.put('/loc/{id}')
async def update_data(loc: Loc, id:int, check: Annotated[bool, Depends(check_is_login)]):
    if not check:
        return
    loc_json = loc.model_dump()
    select_query = "SELECT * FROM locs WHERE id = %s;"
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_query, (id,))
    data = cursor.fetchone()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data loc id {id} Not Found")
    
    query = "UPDATE locs SET latitude=%s, longitude=%s WHERE id = %s;"
    cursor.execute(query, (loc_json["latitude"], loc_json["longitude"], id,))
    conn.commit()

    select_query = "SELECT * FROM locs WHERE id = %s;"
    cursor.execute(select_query, (id,))
    new_loc = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return {
        "messages" : "Update Location successfully",
        "data" : new_loc
    }

@loc.delete('/loc/{id}')
async def delete_data(id: int, check: Annotated[bool, Depends(check_is_admin)]):
    if not check:
        return
    select_query = "SELECT * FROM locs WHERE id = %s;"
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_query, (id,))
    data = cursor.fetchone()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data loc id {id} Not Found")
    
    query = "DELETE FROM locs WHERE id = %s;"
    cursor.execute(query, (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {
        "messages" : "Delete loc successfully",
    }