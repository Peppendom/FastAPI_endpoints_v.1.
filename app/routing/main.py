# Third-party libraries
import uvicorn

# Modules
from app.db import setup
from app.routing.setup import app


if __name__ == "__main__":
    setup.init_db()

    uvicorn.run(
        app = "app.routing.main:app",
        host = "127.0.0.1",
        port = 8000,
        reload = True
    )
