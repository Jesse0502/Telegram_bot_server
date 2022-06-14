from uuid import uuid4
from flask import Blueprint, request, Response
from jose import jwt
from Database import db
import bcrypt
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

overview_blueprint = Blueprint("overview", __name__)


@overview_blueprint.route("/addbot", methods=["POST"])
def addBot():
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    form_data = request.json
    auth_token = request.headers.get("Authorization", None)
    if not auth_token:
        return {"data", "Token Not Found!"}, 400

    jwt_secret = os.getenv("JWT_SECRET")
    user_details = jwt.decode(auth_token.split(" ")[1], jwt_secret)

    if not user_details:
        return {"data": "User not Found!"}, 400

    data = form_data['data']
    coll = db["bots"]
    try:
        bot_exist = coll.find_one({"api_id": data["api_id"]})
        if bot_exist:
            return {"data": "Bot already exists"}, 200

        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        new_bot = {
            "_id": str(uuid4()),
            "owner": str(user_details["_id"]),
            "name": data["name"],
            "api_id": data["api_id"],
            "api_hash": data["api_hash"],
            "password": data["password"],
            "groups": [],
            "status": "Paused",
            "keywords": [],
            "scanGroups": [],
            "output": [],
            "notifications": [],
            "updatedAt": str(dt_string),
            "createdAt": str(dt_string),
        }
        coll.insert_one(new_bot)
        return {"data": "Bot added successfully"}, 200
    except:
        return {"data": "Some Error Occured"}, 500
