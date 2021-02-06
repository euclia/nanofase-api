# from src.globals.globals import mongoClient

class TaskDao():

    def __init__(self, mongoClient):
        self.mongoClient = mongoClient

    def update_task(self, find, update):
        query = {"$and": [{"userId": find['userId']}, {"_id": find['_id']}]}
        try:
            update_dict = {"$set": {"messages": update['messages']
                , "percentage": update["percentage"], "simulationKeys": update["simulationKeys"]}}
            find['messages'] = update['messages']
            find["percentage"] = update["percentage"]
            find["simulationKeys"] = update["simulationKeys"]
        except KeyError as ke:
            update_dict = {
                "$set": {"messages": update['messages'], "percentage": update["percentage"]}}
            find['messages'] = update['messages']
            find["percentage"] = update["percentage"]
        self.mongoClient['task'].update_one(query, update_dict)
        return find

    def update_task_error(self, find, update):
        query = {"$and": [{"userId": find['userId']}, {"_id": find['_id']}]}
        try:
            update = {"$set": {"messages": update['messages'], "percentage": update["percentage"], "error": update["error"]}}
        except KeyError as ke:
            update = {
                "$set": {"messages": update['messages'], "percentage": update["percentage"], "error": update["error"]}}
        self.mongoClient['task'].update_one(query, update)
        return find

    def find_one(self, find):
        query = {"$and": [{"userId": find['userId']}, {"_id": find['_id']}]}
        task = self.mongoClient['task'].find_one(query)
        return task