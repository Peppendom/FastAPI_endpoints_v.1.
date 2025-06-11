# Third-party libraries
from fastapi import FastAPI

# Modules
from app.db import setup
from app.routing import endpoints


setup.init_db()
app = FastAPI()
app.include_router(endpoints.router)
