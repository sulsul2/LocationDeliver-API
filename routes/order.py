from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from db.connection import cursor, conn
from routes.jwt import check_is_admin, check_is_login, get_user
from models.order import Order
from models.user import User

order = APIRouter()

@order.get('/order')
async def read_data(user: Annotated[User, Depends(get_user)]):
    if user['role'] == 'admin':
          query = "SELECT * FROM orders;"
          cursor.execute(query)
          data = cursor.fetchall()
          return {
			"messages" : "Get All order successfully",
			"data" : data
        }
    elif user['role'] == 'user':
        query = "SELECT * FROM orders where user_id = %s"
        cursor.execute(query, (user['id'],))
        cursor.execute(query)
        data = cursor.fetchall()
        return {
			"messages" : "Get Your order successfully",
			"data" : data
        }
    else:
        query = "SELECT * FROM orders where food_id = %s"
        cursor.execute(query, (user['id'],))
        cursor.execute(query)
        data = cursor.fetchall()
        return {
			"messages" : "Get Your order successfully",
			"data" : data
        }

@order.get('/order/{id}')
async def read_data(id: int, check: Annotated[bool, Depends(check_is_login)]):
    if not check:
        return
    select_query = "SELECT * FROM orders WHERE id = %s;"
    cursor.execute(select_query, (id,))
    data = cursor.fetchone()

    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data order id {id} Not Found")
    
    return {
        "messages" : "Get order successfully",
        "data" : data
    }

@order.post('/order')
async def write_data(order: Order, check: Annotated[bool, Depends(check_is_login)], user: Annotated[User, Depends(get_user)]):
    if not check:
        return
    order_json = order.model_dump()
    if (order_json['is_hemat'] == True):
        time = "30 Minutes"
        price = 10000
    else:
        time = "10 Minutes"
        price = 30000
    query = "INSERT INTO orders (time, price, user_id, food_id, is_hemat) VALUES(%s, %s, %s, %s, %s);"
    cursor.execute(query, (time, price, user['id'], order_json['food_id'], order_json['is_hemat']))
    conn.commit()

    select_query = "SELECT * FROM orders WHERE id = LAST_INSERT_ID();"
    cursor.execute(select_query)
    new_order = cursor.fetchone()

    return {
        "messages" : "Add order successfully",
        "data" : new_order
    }
    
@order.put('/order/{id}')
async def update_data(order: Order, id:int, check: Annotated[bool, Depends(check_is_admin)]):
    if not check:
        return
    order_json = order.model_dump()
    select_query = "SELECT * FROM orders WHERE id = %s;"
    cursor.execute(select_query, (id,))
    data = cursor.fetchone()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data order id {id} Not Found")
    
    query = "UPDATE orders SET time=%s, price=%s WHERE id = %s;"
    cursor.execute(query, (order_json["time"], order_json["price"], id,))
    conn.commit()

    select_query = "SELECT * FROM orders WHERE id = %s;"
    cursor.execute(select_query, (id,))
    new_order = cursor.fetchone()
    
    return {
        "messages" : "Update order successfully",
        "data" : new_order
    }

@order.delete('/order/{id}')
async def delete_data(id: int, check: Annotated[bool, Depends(check_is_admin)]):
    if not check:
        return
    select_query = "SELECT * FROM orders WHERE id = %s;"
    cursor.execute(select_query, (id,))
    data = cursor.fetchone()
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data order id {id} Not Found")
    
    query = "DELETE FROM orders WHERE id = %s;"
    cursor.execute(query, (id,))
    conn.commit()
    return {
        "messages" : "Delete order successfully",
    }