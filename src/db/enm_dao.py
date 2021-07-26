# from src.globals.globals import mongoClient

class ENMDao():

    def __init__(self, mongoClient):
        self.mongoClient = mongoClient

    def update_one(self, find, update):
        query = {"$and": [{"userId": find['userId']}, {"_id": find['_id']}]}
        self.mongoClient['ENM'].replace_one(query, update, True)
        return update

    def find_one(self, find):
        query = {"$and": [{"userId": find['userId']}, {"_id": find['_id']}]}
        ENM = self.mongoClient['ENM'].find_one(query)
        return ENM

    def find(self,find):
        query = {"userId": find['userId']}
        ENMs = self.mongoClient['ENM'].find(query).limit(find['maximum'])
        total = self.mongoClient['ENM'].count(query)

        return ENMs, total

    def insert_one(self, ENM):
        self.mongoClient['ENM'].insert_one(ENM)
        return ENM

    def delete_one(self, userId, ENMId):
        self.mongoClient['ENM'].delete_one( {"$and": [{"userId": userId}, {"_id": ENMId}]})
        return id
    