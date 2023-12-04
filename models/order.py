from pydantic import BaseModel

class Order(BaseModel):
	time: str
	price: int
	user_id: int
	food_id: int
	is_hemat: bool
	pesanan_id : int
	shipping_price :int