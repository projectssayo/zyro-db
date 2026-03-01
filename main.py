import string

import requests
from fastapi import FastAPI

from pymongo import MongoClient
import random
import datetime

from pymongo.errors import ServerSelectionTimeoutError

app=FastAPI()

url = r'mongodb+srv://projectssayo_db_user:1234@test.mdv08ad.mongodb.net/?retryWrites=true&w=majority&appName=test'

client = MongoClient(
    url,
    serverSelectionTimeoutMS=3000,
    connectTimeoutMS=3000,
    socketTimeoutMS=3000
)

ui_lock_db = client["ui_lock_db"]
user_db = client["users_db"]

ui_lock_password_table=ui_lock_db["ui_password_table"]
ui_lock_token_table=ui_lock_db["ui_token_table"]
user_table = user_db["user_info"]






@app.get("/set_ui_lock_password")
def set_ui_lock_password(email: str, password: str):
    try:
        a=ui_lock_password_table.update_one(
            {"_id": email},{
                "$set": {
                    "email": email,
                    "password": password
                }
            },upsert=True
        )

        return {
                "success": True,
                "message":f"password of user {email} has been updated successfully at {datetime.datetime.now()}"
            }


    except ServerSelectionTimeoutError:
        return {"success": False, "message": "Server selection timeout, internet nahi hai gareeb bc"}

    except Exception as e:

        return {"message": str(e), "success": False}




def get_random_token():
    hex_chars = "0123456789abcdefanvayaNEGISAYOXYZ"
    return ''.join(random.choice(hex_chars) for _ in range(64))



@app.get("/get_pfp")
def get_pfp(email:str):
    try:
        a=user_table.find_one({"_id": email})['circle_pfp']
        return {'success': True, 'img_link': a}
    except ServerSelectionTimeoutError:
        return {"success": False, "message": "Server selection timeout"}
    except Exception as e:
        return {"message": str(e), "success": False}



@app.get("/generate_token")
def generate_token(email: str):
    try:
        token=get_random_token()

        ui_lock_token_table.delete_many({"email": email})
        ui_lock_token_table.update_one({
            "_id":token
        },
            {"$set":
                 {"email": email,
                  "used":False,
                  "valid":datetime.datetime.now()+datetime.timedelta(minutes=5)
                  }
             },upsert=True
        )

        return {'success': True, 'message':"token generated successfully","token":token}


    except ServerSelectionTimeoutError:
        return {"success": False, "message": "Server selection timeout, internet nahi hai gareeb bc"}

    except Exception as e:

        return {"message": str(e), "success": False}



@app.get("/get_data_from_token")
def get_data_from_token(token: str):
    try:
        a=ui_lock_token_table.find_one({"_id": token})
        if not a:
            return {"success": False, "message": "token does not exist invalid token"}

        if a['used']:
            return {'success':False,"message":"token has been already used to generate password for the user"}
        if datetime.datetime.now()>a['valid']:
            return {'success':False,"message":"token has been expired try regenerating new token"}




        pfp=user_table.find_one({"_id": a['email']})['circle_pfp']

        result={
            "email":a['email'],
            "used":a['used'],
            "pfp":pfp,
            "token":token,
            "valid":a['valid']
        }

        return {'success': True, 'message':"token is successfully verified",'data':result}








    except ServerSelectionTimeoutError:
        return {"success": False, "message": "Server selection timeout, internet nahi hai gareeb bc"}

    except Exception as e:

        return {"message": str(e), "success": False}


@app.get("/update_password_via_token")
def update_password_via_token(token:str, password:str):
    try:
        a=ui_lock_token_table.find_one({"_id": token})
        if not a:
            return {"success": False, "message": "token does not exist invalid token"}
        if a['used']:
            return {'success':False,"message":"token has been already used to generate password for the user"}
        if datetime.datetime.now()>a['valid']:
            return {'success':False,"message":"token has been expired try regenerating new token"}

        b=ui_lock_password_table.update_one({"_id": a['email']},{
            "$set":{
                "password": password,
            }
        },upsert=True
                                         )


        ui_lock_token_table.update_one({"_id":token},{
                "$set":{
                    "used":True
                }
            }
       )
        return {'success':True,'message':f"password of user {a['email']} has been updated successfully at {datetime.datetime.now()}"}


    except ServerSelectionTimeoutError:
        return {"success": False, "message": "server selection timeout, internet nahi hai gareeb bc"}
    except Exception as e:
        return {"message": str(e), "success": False}








@app.get("/")
def info():
    return {
        "/set_ui_lock_password" : 'https://zyro-db.onrender.com//set_ui_lock_password?email=suyognegi1@gmail.com&password=123',
        "/get_pfp":'https://zyro-db.onrender.com//get_pfp?email=suyognegi1@gmail.com',
        "/generate_token":'https://zyro-db.onrender.com//generate_token?email=suyognegi1@gmail.com',
        "/get_data_from_token":'https://zyro-db.onrender.com//get_data_from_token?token=1aOf3c29YGAe9GZff5cd3aeaIYYZY5afI3eZ2SXG2Zd7Yabc1Z9G3e2AOaca3aYX',
        "/update_password_via_token":'https://zyro-db.onrender.com//update_password_via_token?token=1aOf3c29YGAe9GZff5cd3aeaIYYZY5afI3eZ2SXG2Zd7Yabc1Z9G3e2AOaca3aYX&password=my_pass123',

    }






# uvicorn api_0301_1629_lock_ui_for_render:app --port 7711
