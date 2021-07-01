import csv
import pyproj
import pandas as pd
from jaqpotpy import Jaqpot
import time
import multiprocessing
from src.dev.read import read_dev
import asyncio
from multiprocessing import Queue, Process
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

pbdays = 380

# simulationId = "GRQCEgKkNqVGlu"
simulationId = "TunEwRopmTLHFi"
userId = "3abf848d-e297-4e68-8072-2dd1ced89505"
pbpk = True

# jaqpot = Jaqpot('https://modelsbase.cloud.nanosolveit.eu/modelsbase/services/')
# jaqpot.login('pantelispanka', 'kapan2')
# df = jaqpot.get_dataset('1530d5347f7249879e148fdd2071627d')
#
# for index, row in df.iterrows():
#     for index, val in row.iteritems():
#         print(index)
#         print(val)
#
# print(list(df))


def task_process(task, t1q, t2q, t3q, userId):
    p = True
    p1f = False
    p2f = False
    p3f = False
    p = True
    while p:
        if p1f is False:
            t1m = t1q.get()
            # print(p1)
            if t1m == 'Finished':
                print("Sediment output procesing finished. Last update for the Sediment outputs")
                # task = mongoClient['task'].find_one({"_id": task['_id']})
                # task['messages'].append("Sediment output finished")
                # taskDao.update_task(task, task)
                p1f = True
        if p2f is False:
            t2m = t2q.get()
            # print(p2)
            if t2m == 'Finished':
                print("Soil output procesing finished. Last update for the Soil outputs")
                # task = mongoClient['task'].find_one({"_id": task['_id']})
                # task['messages'].append("Soil output finished")
                # taskDao.update_task(task, task)
                p2f = True
        if p3f is False:
            t3m = t3q.get()
            # print(p3)
            if t3m == 'Finished':
                print("Water output procesing finished. Last update for the Water outputs")
                # task = mongoClient['task'].find_one({"_id": task['_id']})
                # task['messages'].append("Water output finished")
                # taskDao.update_task(task, task)
                p3f = True
        if p1f and p2f and p3f:
            print("The simulation finished running. Last update for the Task")
            # task = mongoClient['task'].find_one({"_id":task['_id']})
            # task['messages'].append("Processing outputs finished")
            # task['percentage'] = 100.00
            # taskDao.update_task(task, task)
            if pbpk:
                add_biouptake(simulationId, userId, pbdays)
            p = False
            break

    # sediment_outs = sediment_outs_m
    # water_outs = water_outs_m
    # soil_outs = soil_outs_m

    # sediment_outs = read('/Users/pantelispanka/Desktop/output_sediment.csv', "1", "sediment", 'uis', None, None, True)
    # water_outs = read('/Users/pantelispanka/Desktop/output_water.csv', "1", "water", 'uis', None, None, True)
    # soil_outs = read('/Users/pantelispanka/Desktop/output_soil.csv', "1", "soil", 'uis', None, None, True)


def add_biouptake(simulationId, userId, pbpkDays):
    query = {"simulationId": simulationId}
    water_outs = list(mongoClient['output_water_points'].find(query))
    sediment_outs = list(mongoClient['output_sediment_points'].find(query))
    # soil_outs = mongoClient['output_water_points'].find(query)

    multi_pbpk_dfs = []
    for index, point_output in enumerate(water_outs):
        C_sed = [element * 1000 for element in sediment_outs[index]['C_np_total(kg/kg)']]
        C_Water = [element * 1000 for element in water_outs[index]['C_np(kg/m3)']]
        C_water_dis = [element * 1000 for element in water_outs[index]['C_dissolved(kg/m3)']]
        C_ss = [element * 1000 for element in water_outs[index]['C_spm(kg/m3)']]
        x = water_outs[index]['x']
        y = water_outs[index]['y']
        if len(C_sed) < pbdays:
            for i in range(pbdays - len(C_sed)):
                C_sed.append(0.0)
                C_Water.append(0.0)
                C_water_dis.append(0.0)
                C_ss.append(0.0)

        time_vec = []
        for day in range(pbdays):
            time_vec.append(day + 1)

        multi_pbpk_df = pd.DataFrame(columns=['material', 'sim.step', 'sim.start', 'sim.end', 'C_sed', 'C_Water',
                                              'C_water_dis', 'C_ss', 'time_vec', 'x', 'y'])
        row = {'material': "TiO2", 'sim.step': 1, 'sim.start': 1, 'sim.end': pbdays, 'C_sed': C_sed,
               'C_water': C_Water, 'C_water_dis': C_water_dis, 'C_ss': C_ss, 'time_vec': time_vec, 'x': x, 'y': y}
        multi_pbpk_df = multi_pbpk_df.append(row, ignore_index=True)

        multi_pbpk = {}
        multi_pbpk['df'] = multi_pbpk_df
        multi_pbpk['geometry'] = point_output['geometry']
        multi_pbpk_dfs.append(multi_pbpk)


    for day in range(pbpkDays):
        day_sim = day + 1
        feat_col = {}
        feat_col['type'] = "FeatureCollection"
        feat_col['simulationId'] = simulationId
        feat_col['userId'] = userId
        feat_col['day'] = day_sim
        feat_col['features'] = []
        mongoClient['output_biouptake'].insert_one(feat_col)


    chunks = [multi_pbpk_dfs[x:x + 25] for x in range(0, len(multi_pbpk_dfs), 25)]


    q = multiprocessing.Queue()

    processes = []
    for c in chunks:
        processes.append(multiprocessing.Process(target=create_biouptake, args=(c, simulationId, q)))

    for p in processes:
        p.daemon = False
        p.start()

    p = processes[len(processes) - 1]
    p.join()


def create_biouptake(chunk, simulationId, bqueue):
    jaqpot = Jaqpot('https://modelsbase.cloud.nanosolveit.eu/modelsbase/services/')
    jaqpot.login('pantelispanka', 'kapan2')
    for point in chunk:
        preds, prediction = jaqpot.predict(point['df'], 'YxuV65I02bQkmeY5vWok')
        for index, row in preds.iterrows():
            feat = {}
            props = {}
            props['x'] = point['df']['x'].values[0]
            props['y'] = point['df']['y'].values[0]
            for index, val in row.iteritems():
                if index == 'time':
                    time = val
                    props['t'] = int(val)
                else:
                    props[index] = val
                feat['type'] = 'Feature'
                feat['properties'] = props
                feat['geometry'] = point['geometry']
            query = {"$and": [{"day": int(time)}, {"simulationId": simulationId}]}
            mongoClient['output_biouptake'].find_one_and_update(query, {"$push": {"features": feat}})

    # jaqpot.get_dataset()

# start_time = time.time()
# preds, prediction = jaqpot.predict(chunks[0][0], 'YxuV65I02bQkmeY5vWok')
# print("--- %s seconds ---" % (time.time() - start_time))
#
# print(preds)
# print(prediction)
# print(multi_pbpk_df)


if __name__ == '__main__':
    # add_biouptake(simulationId, userId, pbdays)

    t1q = Queue()
    t2q = Queue()
    t3q = Queue()

    p1 = multiprocessing.Process(target=read_dev, args=('/Users/pantelispanka/Desktop/output_sediment.csv', "GRQCEgKkNqVGlu"
                                                        , "output_sediment", 'uis', None, t1q, True))
    p1.daemon = True
    p1.start()

    p2 = multiprocessing.Process(target=read_dev, args=('/Users/pantelispanka/Desktop/output_water.csv', "GRQCEgKkNqVGlu"
                                                        , "output_water", 'uis', None, t2q, True))
    p2.daemon = True
    p2.start()
    p3 = multiprocessing.Process(target=read_dev, args=('/Users/pantelispanka/Desktop/output_soil.csv', "GRQCEgKkNqVGlu"
                                                        , "output_soil", 'uis', None, t3q, True))
    p3.daemon = True
    p3.start()

    p4 = Process(target=task_process, args=(None, t1q, t2q, t3q, "uId"))
    p4.daemon = False
    p4.start()
    p4.join()


