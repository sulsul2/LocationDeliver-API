from pydantic import BaseModel

class Order(BaseModel):
	time: str
	price: float
	user_id: int
	food_id: int
	is_hemat: bool