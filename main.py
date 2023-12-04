import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.location import loc
from routes.order import order
from routes.auth import auth
from routes.menu import menu

app = FastAPI()

app.include_router(loc)
app.include_router(order)
app.include_router(auth)
app.include_router(menu)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)