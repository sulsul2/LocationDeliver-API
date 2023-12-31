from typing import Annotated, List
import requests
from models.order import Order
from models.user import User
from fastapi import APIRouter, Depends
from routes.auth import get_user
from models.menu import Menu
from routes.order import write_data

menu = APIRouter()

@menu.get('/menu')
async def get_menu(user: Annotated[User, Depends(get_user)]) :
    url = "https://resto-hemat-api.ambitiousmoss-bd081c95.australiaeast.azurecontainerapps.io/menu/stok/"
    headers = {
        "Authorization": f"Bearer {user['friend_token']}"
    }

    try:
        response = requests.get(url, headers=headers)

        data = response.json()

        for row in data :
            if row[3] < 5 :
                row.append(round(row[2] * (3/4)))
            else :
                row.append(row[2])
        
        return {
            "message" : "Get Success",
            "data" : data
        }
    except requests.RequestException as e:
        return("Terjadi kesalahan saat mengakses API:", e)

@menu.post('/pesanan')
async def create_pesanan (data_to_add: List[Menu], is_hemat : bool, user: Annotated[User, Depends(get_user)]) :
    url = "https://resto-hemat-api.ambitiousmoss-bd081c95.australiaeast.azurecontainerapps.io/pesanan/createdata"
    headers = {
        "Authorization": f"Bearer {user['friend_token']}"
    }
    formatted_data = [{"Id": item.Id, "MenuId": item.MenuId, "Jumlah": item.Jumlah} for item in data_to_add]
    input = {
        "Data" : formatted_data,
        "Total" : 20000,
    }

    try:
        response = requests.post(url, json = input, headers=headers)
        data = response.json()

        order_data = {
            "time" : "minutes",
            "price" : data['Total'],
            "user_id" : user['id'],
            "food_id" : 17,
            "is_hemat" : is_hemat,
            "pesanan_id" : data['PesananId'],
            "shipping_price" : 10
        }

        order = Order(**order_data)

        new_order_data = await write_data(order, True, user)

        return {
            "message" : "Get Success",
            "data" : {
                "order_detail": data,
                "delivery_order": new_order_data
            }
        }
    except requests.RequestException as e:
        return("Terjadi kesalahan saat mengakses API:", e)