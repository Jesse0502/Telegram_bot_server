import asyncio
import logging
import threading
from flask import Flask, Response
from Overview_Routes import overview_blueprint
from Authentication_Routes import signup_blueprint
from flask_cors import CORS
from Bots_Routes import bots_blueprint
from Notification_Routes import notification_blueprint
from Database import db
from concurrent import futures

from bot import bot
import logging
app = Flask(__name__)

application = Flask(__name__)
cors = CORS(application)
application.config['CORS_HEADERS'] = 'Content-Type'


@application.route("/")
def starting_url():
    response = Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    return 'Homepage', 200


application.register_blueprint(
    notification_blueprint, url_prefix="/api/notifications")
application.register_blueprint(signup_blueprint, url_prefix="/api/auth")
application.register_blueprint(bots_blueprint, url_prefix="/api/bots")
application.register_blueprint(overview_blueprint, url_prefix="/api")

if __name__ == '__main__':
    application.run(debug=True)
