import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.location import loc
from routes.order import order
from routes.auth import auth

app = FastAPI()

app.include_router(loc)
app.include_router(order)
app.include_router(auth)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)