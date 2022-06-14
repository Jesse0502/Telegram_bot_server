from flask import Blueprint, request, Response
from jose import jwt
from Database import db
import bcrypt
import json
import os
from dotenv import load_dotenv

load_dotenv()

notification_blueprint = Blueprint("notification", __name__)


@notification_blueprint.route("/getNotifications", methods=["POST"])
def getNotification():
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    try:
        auth_token = request.headers.get("Authorization", None)
        if not auth_token:
            return {"data": "Token invalid"}, 400
        jwt_secret = os.getenv("JWT_SECRET")
        user_details = jwt.decode(auth_token.split(" ")[1], jwt_secret)
        if not user_details:
            return {"data": "Token Invalid"}, 400
        coll = db["bots"]
        res = coll.find_one({"owner": user_details["_id"]})
        if res:
            
            return {"data": res["notifications"]}, 200
        return {"data": "Some error occured"}, 500

    except Exception as e:
        print(e)
        return {"data": "Some error occured"}, 500
