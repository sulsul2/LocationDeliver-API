import uvicorn
from fastapi import FastAPI

from routes.location import loc
from routes.order import order
from routes.auth import auth

app = FastAPI()

app.include_router(loc)
app.include_router(order)
app.include_router(auth)