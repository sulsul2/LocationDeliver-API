from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from routes.jwt import check_is_admin, check_is_login, get_user
from models.order import Order
from models.user import User
from math import radians, sin, cos, sqrt, atan2
from db.connection import connectDB

def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Calculate the change in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine formula to calculate distance between two points
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Calculate the distance
    distance = R * c
    return distance

order = APIRouter()

@order.get('/order')
async def read_data(user: Annotated[User, Depends(get_user)]):
    print(user['role'])
    print(user['id'])
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    if user['role'] == 'admin':
          query = "SELECT * FROM orders;"
          cursor.execute(query)
          data = cursor.fetchall()
          cursor.close()
          conn.close()
          return {
			"messages" : "Get All order successfully",
			"data" : data
        }
    elif user['role'] == 'user':
        query = "SELECT * FROM orders where user_id = %s"
        cursor.execute(query, (user['id'],))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        if data :
            return {
                "messages" : "Get Your order successfully",
                "data" : data
            }
        else :
            return {
                "messages" : "You don't have ordered yet please make an order first"
            }
    else:
        query = "SELECT * FROM orders where food_id = %s"
        cursor.execute(query, (user['id'],))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return {
			"messages" : "Get Your order successfully",
			"data" : data
        }

@order.get('/order/{id}')
async def read_data(id: int, check: Annotated[bool, Depends(check_is_login)]):
    if not check:
        return
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    select_query = "SELECT * FROM orders WHERE id = %s;"
    cursor.execute(select_query, (id,))
    data = cursor.fetchone()
    cursor.close()
    conn.close()

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
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)

    time = await get_order_time(order_json['food_id'], order_json['is_hemat'], True, user)
    shipping_price = await get_order_price(order_json['food_id'], order_json['is_hemat'], True, user)

    time_string = f"{time} menit"
    query = "INSERT INTO orders (time, price, user_id, food_id, is_hemat, pesanan_id, shipping_price) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(query, (time_string, order_json['price'], user['id'], order_json['food_id'], True, order_json['pesanan_id'], shipping_price,))
    conn.commit()

    select_query = "SELECT * FROM orders WHERE id = LAST_INSERT_ID();"
    cursor.execute(select_query)
    new_order = cursor.fetchone()
    cursor.close()
    conn.close()

    return {
        "messages" : "Add order successfully",
        "data" : new_order
    }
    
@order.put('/order/{id}')
async def update_data(order: Order, id:int, check: Annotated[bool, Depends(check_is_admin)]):
    if not check:
        return
    order_json = order.model_dump()
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
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

    cursor.close()
    conn.close()
    
    return {
        "messages" : "Update order successfully",
        "data" : new_order
    }

# @order.delete('/order/{id}')
# async def delete_data(id: int, check: Annotated[bool, Depends(check_is_admin)]):
#     if not check:
#         return
#     conn = connectDB()
#     cursor = conn.cursor(dictionary=True)
#     select_query = "SELECT * FROM orders WHERE id = %s;"
#     cursor.execute(select_query, (id,))
#     data = cursor.fetchone()
#     if data is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data order id {id} Not Found")
    
#     query = "DELETE FROM orders WHERE id = %s;"
#     cursor.execute(query, (id,))
#     conn.commit()

#     cursor.close()
#     conn.close()
#     return {
#         "messages" : "Delete order successfully",
#     }

@order.get('/order/price/{id}')
async def get_order_price(id: int, hemat: bool, check: Annotated[bool, Depends(check_is_login)], user: Annotated[User, Depends(get_user)]):
    if not check:
        return
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    select_query = "SELECT * FROM locs WHERE id = %s;"
    cursor.execute(select_query, (user['loc_id'],))
    data1 = cursor.fetchone()

    select_query = "SELECT * FROM users WHERE id = %s;"
    cursor.execute(select_query, (id,))
    user2 = cursor.fetchone()

    select_query = "SELECT * FROM locs WHERE id = %s;"
    cursor.execute(select_query, (user2['loc_id'],))
    data2 = cursor.fetchone()

    cursor.close()
    conn.close()

    if (calculate_distance(data1['latitude'],data1['longitude'],data2['latitude'],data2['longitude'])) * 2000 > 50000 :
        price = 50000
    else : 
        price = calculate_distance(data1['latitude'],data1['longitude'],data2['latitude'],data2['longitude']) * 2000
    if hemat :
        price = price / 2
    else :
        price = price
    return price


@order.get('/order/time/{id}')
async def get_order_time(id: int, hemat: bool, check: Annotated[bool, Depends(check_is_login)], user: Annotated[User, Depends(get_user)]):
    if not check:
        return
    conn = connectDB()
    cursor = conn.cursor(dictionary=True)
    select_query = "SELECT * FROM locs WHERE id = %s;"
    cursor.execute(select_query, (user['loc_id'],))
    data1 = cursor.fetchone()

    select_query = "SELECT * FROM users WHERE id = %s;"
    cursor.execute(select_query, (id,))
    user2 = cursor.fetchone()

    select_query = "SELECT * FROM locs WHERE id = %s;"
    cursor.execute(select_query, (user2['loc_id'],))
    data2 = cursor.fetchone()

    cursor.close()
    conn.close()

    if (calculate_distance(data1['latitude'],data1['longitude'],data2['latitude'],data2['longitude'])) / 0.6 > 60 :
        time = 60
    else : 
        time = round(calculate_distance(data1['latitude'],data1['longitude'],data2['latitude'],data2['longitude']) / 0.6)
    if hemat :
        time = time * 2
    else :
        time = time
    return time


    