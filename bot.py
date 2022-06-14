from cmath import exp
from datetime import datetime
import os
import threading
from uuid import uuid4, uuid5
from jinja2 import Undefined
from telethon.sync import TelegramClient
from telethon import events
from concurrent import futures
import asyncio
from Database import db
from telethon.utils import get_display_name


class bot:

    def __init__(self):
        self.run_bot()

    def init_bot(self, name, api_id, api_hash, bot_id):
        try:
            print("inside self.init_bot")
            client = TelegramClient(
                name, int(api_id), api_hash)
            client.start(password=str(bot_id))
            initChannels = []
            for chnl in client.get_dialogs():
                groupName, groupId = (get_display_name(
                    chnl.entity), chnl.entity.id)
                initChannels.append({"name": groupName, "id": str(groupId)})
                db["bots"].find_one_and_update(
                    {"api_id": api_id}, {"$set": {"groups": initChannels}})

            @client.on(events.NewMessage(pattern=""))
            async def get(event):
                try:
                    channels = []
                    stat = db["bots"].find_one({"api_id": api_id})
                    if not stat or stat.get("status", "Paused") == "Paused":
                        client.log_out()

                    for chnl in await client.get_dialogs():
                        groupName, groupId = (get_display_name(
                            chnl.entity), chnl.entity.id)
                        channels.append(
                            {"name": groupName, "id": str(groupId)})

                    db["bots"].find_one_and_update(
                        {"api_id": api_id}, {"$set": {"groups": channels}}, upsert=False)

                    if len(stat.get("groups", [])) < len(channels):
                        for c in channels:
                            if c not in stat["groups"]:
                                now = datetime.now()
                                dt_string = now.strftime(
                                    "%d/%m/%Y %H:%M:%S")
                                db["bots"].find_one_and_update({"api_id": api_id}, {"$set": {
                                    "notifications": [*stat.get("notifications", []), {
                                        "id": str(uuid4()),
                                        "source": f"#New Group Created",
                                        "name": name,
                                        "who_posted": {"id": -1, "first_name": {c["name"]}, "last_name": ""},
                                        "lastUpdated": dt_string,
                                        "description": f"New Group Created:- '{c['name']}'",
                                        "botId": stat["_id"],
                                        "media": None
                                    }]
                                }})

                    global user_id
                    global channel_id
                    user_id = None
                    channel_id = None
                    try:
                        user_id = event.message.peer_id.user_id
                    except Exception as e:
                        pass
                    try:
                        channel_id = event.message.peer_id.channel_id
                    except Exception as e:
                        pass

                    for ch in channels:
                        if ch["id"] == str(channel_id) or ch["id"] == str(user_id):
                            for k in stat["keywords"]:
                                if k in event.message.message:
                                    fileId = uuid4()
                                    global resp
                                    resp = None

                                    who_posted = None
                                    if event.message.from_id:
                                        get_sender = await event.get_sender()
                                        who_posted = {
                                            "id": get_sender.id, "first_name": get_sender.first_name, "last_name": get_sender.last_name}
                                    group_id = str(channel_id) or str(user_id)
                                    data_time = event.message.date
                                    text = event.message.message
                                    if event.message.media:
                                        resp = await client.download_media(file=f"{group_id}/{fileId}", message=event.message)
                                    now = datetime.now()
                                    dt_string = now.strftime(
                                        "%d/%m/%Y %H:%M:%S")
                                    print("------------------")
                                    print(stat)
                                    print({**stat["output"]})
                                    print(stat["output"])
                                    print(
                                        [*stat["output"].get(f"{group_id}", list([]))])
                                    print(stat["output"].get(
                                        f"{group_id}", list([])))
                                    print([*stat.get("notifications", list([]))])
                                    print(stat.get("notifications", list([])))

                                    try:
                                        db["bots"].find_one_and_update({"api_id": api_id}, {"$set": {
                                            "output": {
                                                **stat["output"],
                                                group_id: [
                                                    *stat["output"].get(f"{group_id}", list([])), {
                                                        "sender": who_posted,
                                                        "date_time": data_time,
                                                        "text": text,
                                                        "media": resp
                                                    }]
                                            },
                                            "notifications": [*stat.get("notifications", list([])), {
                                                "id": str(uuid4()),
                                                "source": f"https://web.telegram.org/z/#{group_id if group_id else ''}",
                                                "name": name if name else "None",
                                                "who_posted": who_posted if who_posted else None,
                                                "lastUpdated": dt_string if dt_string else "",
                                                "description": event.message.message,
                                                "botId": stat["_id"] if stat["_id"] else "",
                                                "media": resp if resp else None
                                            }]
                                        }})
                                    except Exception as e:
                                        print("Error from exception -> ", e)
                except Exception as e:
                    pass
                    print(e)

            client.run_until_disconnected()
        except Exception as e:
            pass
            # print(e)

    def worker(self, name, api_id, api_hash, bot_id, loop):
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.init_bot(
                name, api_id, api_hash, bot_id).start())
        except Exception as e:
            pass
            print(e)

    def run_bot(self):
        print("insdie bot")
        try:
            all_bots = []
            for bot in db["bots"].find({"status": "Active"}):
                all_bots.append({"name": bot.get("name", None), "api_id": bot.get("api_id", None), "api_hash": bot.get(
                    "api_hash", None), "bot_id": bot.get("password", None)})
            threads = []
            for b in all_bots:
                loop = asyncio.new_event_loop()
                if loop:
                    t1 = threading.Thread(target=self.worker,
                                          args=(*b.values(), loop))
                    t1.start()
                    threads.append(t1)
            for t in threads:
                t.join()
        except Exception as e:
            # print(e)
            pass
