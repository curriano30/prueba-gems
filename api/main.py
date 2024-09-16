from fastapi import FastAPI
from routes.endpoints import router

app = FastAPI()

app.include_router(router)