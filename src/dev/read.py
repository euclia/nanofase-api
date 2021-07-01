import csv
import pyproj
import pymongo
from src.db.task_dao import TaskDao

class MONGO(object):

    URI = ""
    mongousename = ""
    mongopass = ""
    database = ""

    def __init__(self , mongouri=None, mongopass=None, mongousername=None, database=None):
        print("Starting with mongo at " + mongouri)
        self.URI = mongouri
        self.mongopass = mongopass
        self.mongousename = mongousername
        self.database = database

    # @staticmethod
    def init(self):
        client = pymongo.MongoClient(self.URI)
        if self.database is not None:
            client = client[self.database]
        else:
            client = client['nano-fase']
        return client

mongouri = 'mongodb://127.0.0.1:27017'
mongoClient = MONGO(mongouri=mongouri).init()

taskDao = TaskDao(mongoClient=mongoClient)


def read_dev(csv_f, simulationId, type, userId, task, queue, pbpk=False):
    project = pyproj.Proj("EPSG:27700")
    point_outputs = []
    with open(csv_f, newline='', mode='r') as csvfile:
        csv_reader = csv.reader(csvfile)
        i = -1
        for row in csv_reader:
            try:
                if int(row[0]) != i:
                    day = "changed"
            except ValueError:
                if row[0] == 't':
                    keys = {}
                    for j in range(len(row)):
                        keys[j] = row[j]
                        j += 1
                    i = 1
                    day = "changed"
            if len(row) > 8 and i > -1 and row[0] != 't':

                if day == "changed":
                    try:
                        if pbpk:
                            if len(point_outputs) == 0:
                                for feat in feat_col['features']:
                                    point_output = {}
                                    point_output['x'] = feat['properties']['x']
                                    point_output['y'] = feat['properties']['y']
                                    point_output['geometry'] = feat['geometry']
                                    if next((x for x in point_outputs if
                                             x['x'] == feat['properties']['x'] and x['y'] == feat['properties']['y']),
                                            None) == None:
                                        point_outputs.append(point_output)
                                for index, value in enumerate(point_outputs):
                                    feat = next((feat for feat in feat_col['features'] if
                                                 value['x'] == feat['properties']['x'] and value['y'] ==
                                                 feat['properties']['y']),
                                                None)
                                    for k, v in feat['properties'].items():
                                        if k != 'x' and k != 'y':
                                            try:
                                                value[k].append(v)
                                            except KeyError as e:
                                                value[k] = []
                                                value[k].append(v)
                                            point_outputs[index] = value
                            else:
                                for index, value in enumerate(point_outputs):
                                    feat = next((feat for feat in feat_col['features'] if
                                                 value['x'] == feat['properties']['x'] and value['y'] ==
                                                 feat['properties']['y']),
                                                None)
                                    for k, v in feat['properties'].items():
                                        if k != 'x' and k != 'y':
                                            try:
                                                value[k].append(v)
                                            except KeyError as e:
                                                value[k] = []
                                                value[k].append(v)
                                            point_outputs[index] = value
                        # mongoClient[type].insert_one(feat_col)

                        # taskNew = taskDao.find_one(task)
                        # taskNew['simulationKeys'].append(type + "_day_" + str(i))
                        # taskNew['percentage'] = task['percentage'] + 0.09
                        # task = taskDao.update_task(task, taskNew)

                        feat_col = {}
                        feat_col['type'] = "FeatureCollection"
                        feat_col['userId'] = userId
                        feat_col['simulationId'] = simulationId
                        feat_col['day'] = int(row[0])
                        feat_col['outputType'] = type
                        feat_col['features'] = []
                        i = int(row[0])
                        feat = {}
                        feat['type'] = "Feature"
                        geometry = {}
                        geometry['type'] = "Point"
                        props = {}
                        for k in range(len(row)):
                            try:
                                props[keys[k]] = int(row[k])
                            except ValueError:
                                try:
                                    props[keys[k]] = float("{:.28f}".format(float(row[k])))
                                    # props[keys[k]] = float(row[k])
                                except ValueError:
                                    props[keys[k]] = row[k]
                            if keys[k] == 'easts':
                                easts = row[k]
                            if keys[k] == 'norths':
                                norths = row[k]

                        lon, lat = project(props['easts'], props['norths'], inverse=True)
                        feat['properties'] = props
                        st_end = [round(lon - 0.02, 4), round(lat - 0.018, 4)]
                        geom = {"type": "Polygon", "coordinates": [[st_end, [round(lon - 0.02, 4), round(lat + 0.02, 4)]
                                                                       , [round(lon + 0.03, 4), round(lat + 0.02, 4)],
                                                                    [round(lon + 0.03, 4), round(lat - 0.018, 4)],
                                                                    st_end]]}
                        feat['geometry'] = geom

                        feat_col['features'].append(feat)
                        feat_col['day'] = int(row[0])
                        day = "same"
                    except UnboundLocalError as e:
                        feat_col = {}
                        feat_col['type'] = "FeatureCollection"
                        feat_col['simulationId'] = simulationId
                        feat_col['day'] = int(row[0])
                        feat_col['features'] = []
                        i = int(row[0])
                        feat = {}
                        feat['type'] = "Feature"
                        geometry = {}
                        geometry['type'] = "Point"
                        props = {}
                        for k in range(len(row)):
                            try:
                                props[keys[k]] = int(row[k])
                            except ValueError:
                                try:
                                    props[keys[k]] = float("{:.28f}".format(float(row[k])))
                                    # props[keys[k]] = float(row[k])
                                except ValueError:
                                    props[keys[k]] = row[k]
                            if keys[k] == 'easts':
                                easts = row[k]
                            if keys[k] == 'norths':
                                norths = row[k]
                        lon, lat = project(props['easts'], props['norths'], inverse=True)
                        feat['properties'] = props
                        st_end = [round(lon - 0.02, 4), round(lat - 0.018, 4)]
                        geom = {"type": "Polygon", "coordinates": [[st_end, [round(lon - 0.02, 4), round(lat + 0.02, 4)]
                                                                       , [round(lon + 0.03, 4), round(lat + 0.02, 4)],
                                                                    [round(lon + 0.03, 4), round(lat - 0.018, 4)],
                                                                    st_end]]}
                        feat['geometry'] = geom
                        feat_col['features'].append(feat)
                        feat_col['day'] = int(row[0])
                        day = "same"
                else:
                    i = int(row[0])
                    feat = {}
                    feat['type'] = "Feature"
                    geometry = {}
                    geometry['type'] = "Point"
                    props = {}
                    for k in range(len(row)):
                        try:
                            props[keys[k]] = int(row[k])
                        except ValueError:
                            try:
                                # props[keys[k]] = float(row[k])
                                props[keys[k]] = float("{:.28f}".format(float(row[k])))
                            except ValueError:
                                props[keys[k]] = row[k]
                        if keys[k] == 'easts':
                            easts = row[k]
                        if keys[k] == 'norths':
                            norths = row[k]
                    lon, lat = project(props['easts'], props['norths'], inverse=True)
                    feat['properties'] = props
                    st_end = [round(lon - 0.02, 4), round(lat - 0.018, 4)]
                    geom = {"type": "Polygon", "coordinates": [[st_end, [round(lon - 0.02, 4), round(lat + 0.02, 4)]
                                                                   , [round(lon + 0.03, 4), round(lat + 0.02, 4)],
                                                                [round(lon + 0.03, 4), round(lat - 0.018, 4)],
                                                                st_end]]}
                    feat['geometry'] = geom
                    feat_col['features'].append(feat)
                    day = "same"
    if pbpk:
        for point in point_outputs:
            point['simulationId'] = simulationId
            # mongoClient[type + "_points"].insert_one(point)
    queue.put("Finished")
    return point_outputs