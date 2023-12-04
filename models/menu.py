from pydantic import BaseModel

class Menu (BaseModel):
    Id: int
    MenuId : int
    Jumlah : int
