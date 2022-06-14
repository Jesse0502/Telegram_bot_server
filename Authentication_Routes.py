from uuid import uuid4
from flask import Blueprint, request, Response
from jose import jwt
from Database import db
import bcrypt
import json
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
load_dotenv()

signup_blueprint = Blueprint("signup", __name__)


@signup_blueprint.route("/signup", methods=["POST"])
def signup():
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    form_data = request.json
    data = form_data['data']
    coll = db["users"]
    user_exists = coll.find_one({"email": data['email']})
    if not user_exists:
        try:
            hash_password = bcrypt.hashpw(
                data.get('Password', data["password"]).encode('utf8'), bcrypt.gensalt(10))
            coll.insert_one(
                {"_id": str(uuid4()), "name": data["name"], "email": data["email"], "password": hash_password, "notifications": []})
            return {"data": "User signed up successfully"}, 200
        except:
            return {"data": "Some error occurred"}, 500
    return {"data": "User with this email already exists"}, 200


@signup_blueprint.route("/login", methods=["POST"])
def login():
    print("inside login")
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    form_data = request.json
    data = form_data['data']
    coll = db['users']
    try:
        user_exist = coll.find_one({"email": data["email"]})
        if user_exist:

            compare_pass = bcrypt.checkpw(
                data["password"].encode('utf8'), user_exist["password"])

            if compare_pass:
                jwt_secret = os.getenv("JWT_SECRET")
                token = jwt.encode(
                    {
                        '_id': str(user_exist['_id']),
                        'name': user_exist['name'],
                        'email': user_exist['email'],
                    }, jwt_secret)
                response.headers["Authorization"] = token
                return {"data": token}, 200
        return {"data": "Either password or email is incorrect!"}, 200
    except:
        return {"data": "Some error occurred"}, 500
