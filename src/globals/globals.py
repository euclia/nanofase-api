import os
from .mongodb import MONGO
from flask_oidc import OpenIDConnect

try:
    os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
except EnvironmentError as e:
    print(e)

try:
    mongouri = os.environ['MONGO_URI']
except KeyError as ke:
    mongouri = 'mongodb://127.0.0.1:27017'

try:
    data_path = os.environ['DATA_PATH']
except KeyError as key:
    data_path = '/home/upci/Desktop/nanofase-api/src/data'


try:
    model_files = os.environ['MODEL_DATA']
except KeyError as ke:
    model_files = '/home/upci/Desktop/nanofase-api/src/data/model/data/constants/thames_tio2_2015/'


try:
    model_vars = os.environ['MODEL_VARS']
except KeyError as ke:
    model_vars = '/home/upci/Desktop/nanofase-api/src/data/model/data/model_vars.yaml'

try:
    model_config = os.environ['MODEL_CONFIG']
except KeyError as ke:
    model_config = '/home/upci/Desktop/nanofase-api/src/data/config.nml'

try:
    model_path = os.environ['MODEL_PATH']
except KeyError as ke:
    model_path = '/home/upci/Desktop/nanofase/bin/main'


oidc = OpenIDConnect()
mongoClient = MONGO(mongouri=mongouri).init()
