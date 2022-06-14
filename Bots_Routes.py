import asyncio
from multiprocessing.dummy import Process
import re
import threading
from flask import Blueprint, request, Response, send_file
from jose import jwt
from Database import db
import bcrypt
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from bot import bot
from flask import current_app as app
import zipfile
import io

load_dotenv()

bots_blueprint = Blueprint("bots", __name__)


@bots_blueprint.route("/getBots", methods=["POST"])
def getBots():
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    auth_token = request.headers.get("Authorization", None)
    if not auth_token:
        return {"data", []}, 400

    jwt_secret = os.getenv("JWT_SECRET")
    user_details = jwt.decode(auth_token.split(" ")[1], jwt_secret)
    if not user_details:
        return {"data": []}, 400
    try:
        coll = db["bots"].find({"owner": user_details["_id"]})
        all_bots = []
        for doc in coll:
            all_bots.append(doc)
        return {"data": all_bots}, 200
    except:
        return {"data", []}, 500


@bots_blueprint.route("/delete", methods=["POST"])
def deleteBot():
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    req_data = request.json
    data = req_data['data']
    try:
        coll = db["bots"].find_one({"_id": data["_id"]})
        if coll:
            res = db["bots"].delete_one({"_id": data["_id"]})
            if res:
                return {"data": "Bot Deleted Successfully!"}, 200
        return {"data": "Some error occured"}, 500
    except:
        return {"data", "Some error occured"}, 500


@bots_blueprint.route("/update", methods=["POST"])
async def updateBot():
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    req_data = request.json
    auth_token: str = request.headers.get("Authorization", None)
    if not auth_token:
        return {"data": "Auth Token Not Found! Try logging again!"}, 400

    jwt_secret = os.getenv("JWT_SECRET")
    user_details = jwt.decode(auth_token.split(" ")[1], jwt_secret)

    if not user_details:
        return {"data": "User not Found!"}, 400
    try:
        data = req_data['data']
        is_status = data.get("status", None)
        id = request.args.get("id")
        coll = db["bots"].find_one({"_id": id})
        if coll:
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            res = db["bots"].find_one_and_update(
                {"_id": id}, {'$set': {**data, "updatedAt": str(dt_string)}})
            if res:
                if is_status:
                    threading.Thread(target=bot).start()
                    # threading.Thread(target=await bot).start()
                    # bot()
                    # t = threading.Thread(target=/
                return {"data": "Bot updated Successfully!"}, 200
        return {"data": "Some error occured"}, 500
    except Exception as r:
        print(r)
        return {"data", "Some error occured"}, 500


@bots_blueprint.route("/download", methods=["POST"])
def downloadData():
    try:
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        req_data = request.json

        if not len(req_data["options"]):
            return {"data": "Must provide atleast one extention"}, 400
        auth_token: str = request.headers.get("Authorization", None)
        if not auth_token:
            return {"data": "Auth Token Not Found! Try logging again!"}, 400
        jwt_secret = os.getenv("JWT_SECRET")
        user_details = jwt.decode(auth_token.split(" ")[1], jwt_secret)

        if not user_details:
            return {"data": "User not Found!"}, 400

        bot_data = db["bots"].find_one({"_id": request.args.get("id", None)})
        isFile = os.path.isdir(req_data["group"]["id"])
        if isFile:
            if bot_data:
                f = open(f'{req_data["group"]["id"]}/messages.json', "w+")

                f.write(json.dumps(
                        bot_data["output"], indent=4, sort_keys=True, default=str))
                f.close()

            zf = zipfile.ZipFile("download.zip", "w")
            zf.close()

            zf = zipfile.ZipFile("download.zip", "w")
            for dirname, subdirs, files in os.walk(os.getcwd()):
                splitDir = dirname.split("\\")[-1]
                if splitDir == req_data["group"]["id"]:
                    zf.write(dirname)
                    for filename in files:
                        path = os.path.join(dirname, filename)
                        size = os.stat(path).st_size  # in bytes
                        size = size / 1000000
                        if filename == "messages.json" and size < float(req_data["size"]):
                            zf.write(os.path.join(dirname, filename))
                        for o in req_data["options"]:
                            # req_data["size"]
                            if filename.split(".")[1] == o[1:] and size < float(req_data["size"]):
                                zf.write(os.path.join(dirname, filename))

            zf.close()
        else:
            zf = zipfile.ZipFile("download.zip", "w")
            zf.close()

        return send_file("download.zip"), 200
    except Exception as e:
        print(e)
        return {"data": "Some error occured"}, 500


@bots_blueprint.route("/saveCheckboxes", methods=["POST"])
def saveCheckBoxes():
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    req_data = request.json
    bot_id = request.args.get("id", None)

    if not bot_id:
        return {"data": "No id provided"}, 400
    newData = {

        "id": req_data["data"]["group"]["id"],
        "name": req_data["data"]["group"]["name"],
        "checkBoxes": req_data["data"]["options"]
    }

    try:

        res = db["bots"].find_one({"_id": bot_id})

        res = db["bots"].find_one_and_update({"_id": bot_id}, {"$set": {
            f"checkBoxes.{newData['id']}": newData["checkBoxes"]

        }})
        if res:
            return {"data": "Checkbox saved successfully!"}, 200
        return {"data": "Some error occured"}, 500
    except Exception as e:
        print(e)
        return {"data", "Some error occured"}, 500
