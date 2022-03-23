import motor.motor_asyncio
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from server.response_helper import *

from server.models.users import *

router = APIRouter()

class Settings(BaseModel):
    authjwt_secret_key: str='e8ae5c5d5cd7f0f1bec2303ad04a7c80f09f759d480a7a5faff5a6bbaa4078d0'


@AuthJWT.load_config
def get_config():
    return Settings()

# mongo conf
MONGO_DETAILS = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

payment = client.payment_db
users_collection = payment.get_collection("users")


@router.post("/register", response_description="Data added into the database")
async def register(users: UsersSchema = Body(...)):
    users = jsonable_encoder(users)
    check_phone_number = await users_collection.find_one({"phone_number": users.get("phone_number")})
    if check_phone_number:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone Number already registered")
    else:
        new_users = await users_collection.insert_one(users)
        new_users = await users_collection.find_one({"_id": new_users.inserted_id})
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=users_helper(new_users))


# Standard login endpoint. Will return a fresh access token and a refresh token
@router.post("/login", response_description="Login user")
async def login(login: UserLoginSchema = Body(...), Authorize:AuthJWT = Depends()):
    login = jsonable_encoder(login)
    validation_login = await users_collection.find_one({"phone_number": login.get("phone_number")})
    if validation_login:
        if validation_login["pin"] == login.get("pin") and validation_login["phone_number"] == login.get("phone_number"):
            access_token = Authorize.create_access_token(subject=login.get("phone_number"), fresh=True)
            refresh_token = Authorize.create_refresh_token(subject=login.get("phone_number"))
            return JSONResponse(status_code=status.HTTP_200_OK, content=login_helper({"access_token":access_token,"refresh_token":refresh_token}))
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=login_phone_number_helper())
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=login_phone_number_helper())


# Any valid JWT access token can access this endpoint
@router.get("/validation_token", response_description="Get phone number from current user")
def get_logged_in_user(Authorize:AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    current_user=Authorize.get_jwt_subject()
    return {"current_user":current_user}


@router.get("/new_token", response_description="Get new access token")
def create_new_token(Authorize:AuthJWT=Depends()):
    """
    new_token token endpoint. This will generate a new access token from
    the refresh token, but will mark that access token as non-fresh,
    as we do not actually verify a password in this endpoint.
    """
    try:
        Authorize.jwt_refresh_token_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    current_user = Authorize.get_jwt_subject()
    access_token = Authorize.create_access_token(subject=current_user, fresh=False)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"new_access_token":access_token})


@router.post("/login_new_token", response_description="Get new access token")
async def login_new_token(login: UserLoginSchema = Body(...), Authorize:AuthJWT = Depends()):
    """
    Fresh login endpoint. This is designed to be used if we need to
    make a fresh token for a user (by verifying they have the
    correct username and password). Unlike the standard login endpoint,
    this will only return a new access token, so that we don't keep
    generating new refresh tokens, which entirely defeats their point.
    """
    login = jsonable_encoder(login)
    validation_login = await users_collection.find_one({"phone_number": login.get("phone_number")})
    if validation_login:
        if validation_login["pin"] == login.get("pin") and validation_login["phone_number"] == login.get("phone_number"):
            new_access_token = Authorize.create_access_token(subject=login.get("phone_number"), fresh=True)
            return JSONResponse(status_code=status.HTTP_200_OK, content=({"new_access_token":new_access_token}))
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone Number and pin does not match")


# Only fresh JWT access token can access this endpoint
@router.get("/new_validation_token", response_description="Get new validation token")
def create_new_validation_token(Authorize:AuthJWT=Depends()):
    try:
        Authorize.fresh_jwt_required()
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    current_user = Authorize.get_jwt_subject()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"current_user":current_user})