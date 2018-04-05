import os
import logging

import zmq

from flask import Flask
from flask.ext import restful
from flask.ext.mongoengine import MongoEngine
from flask.ext.security import Security, MongoEngineUserDatastore

from app.models import User, Role, Configuration
from app.daemon import MassiveDaemon

application = Flask(__name__, static_url_path='')

# os.urandom(24)
application.secret_key = b'\x9b\x8c[\x82}\xbdy-\n+Dy<\xff\x99\xf4\r\x9a\xa7\x92\x97\xa0!-'

application.config.from_object('config')
application.config['MONGODB_SETTINGS'] = {
    'DB': 'fancyMushroom',
    'HOST': '127.0.0.1',
    'PORT': 27017
}

logging.basicConfig(level=logging.INFO)
application.logger.setLevel(logging.INFO)

db = MongoEngine(application)
api = restful.Api(application)

# Setup Flask-Security

user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(application, user_datastore)

##initialize zmq socket
port = 7778
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

#import application
import app.views
import app.auth

