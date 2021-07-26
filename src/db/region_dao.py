# from src.globals.globals import mongoClient

class RegionDao():

    def __init__(self, mongoClient):
        self.mongoClient = mongoClient

    def update_one(self, find, update):
        query = {"$and": [{"userId": find['userId']}, {"_id": find['_id']}]}
        self.mongoClient['region'].replace_one(query, update, True)
        return update

    def find_one(self, find):
        query = {"$and": [{"userId": find['userId']}, {"_id": find['_id']}]}
        region = self.mongoClient['region'].find_one(query)
        return region

    def find(self,find):
        query = {"userId": find['userId']}
        regions = self.mongoClient['region'].find(query).limit(find['maximum'])
        total = self.mongoClient['region'].count(query)

        return regions, total

    def insert_one(self, region):
        self.mongoClient['region'].insert_one(region)
        return region

    def delete_one(self, userId, regionId):
        self.mongoClient['region'].delete_one( {"$and": [{"userId": userId}, {"_id": regionId}]})
        return id
    