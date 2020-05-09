import os
from .mongodb import MONGO
from flask_oidc import OpenIDConnect


try:
    mongouri = os.environ['MONGO_URI']
except KeyError as ke:
    mongouri = 'mongodb://127.0.0.1:27017'

oidc = OpenIDConnect()

mongoClient = MONGO(mongouri=mongouri).init()

