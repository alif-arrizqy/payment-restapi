from datetime import datetime

def users_helper(users) -> dict:
    created_date = users["created_date"].replace("T", " ")[:-7]
    return {
        "status": "SUCCESS",
        "result": {
            "user_id": str(users["user_id"]),
            "first_name": users["first_name"],
            "last_name": users["last_name"],
            "phone_number": users["phone_number"],
            "address": users["address"],
            "pin": users["pin"],
            "created_date": str(datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S').strftime('%Y/%m/%d %H:%M:%S'))
        }
    }

def login_phone_number_helper() -> dict:
    return {
        "message": "Phone Number and pin does not match"
    }

def login_helper(login) -> dict:
    return {
        "status": "SUCCESS",
        "result": {
            "access_token": login["access_token"],
            "refresh_token": login["refresh_token"],
        }
    }

