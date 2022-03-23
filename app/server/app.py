from fastapi import FastAPI
from server.routes.base import api_router


def include_router(app):
    app.include_router(api_router)


def start_app():
    app = FastAPI()
    include_router(app)
    return app

app = start_app()
