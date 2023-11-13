from pydantic import BaseModel

class Loc(BaseModel):
	latitude: float
	longitude: float