from fastapi import APIRouter
from server.routes.apis import route_users


api_router = APIRouter()
api_router.include_router(route_users.router, tags=["Users"])
