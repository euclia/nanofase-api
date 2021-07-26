# from flask import request
# from flask_restx import reqparse, fields,  Namespace, Resource
# from flask import Response
# from src.globals.globals import oidc, mongoClient
# from src.simulation import run_simulation
# from functools import wraps
# from bson import json_util
# import json
# import string
# import random
# from multiprocessing import Process


# simulationsNamespace = Namespace('simulation')

# parser = reqparse.RequestParser()
# parser.add_argument('skip', type=int, help='skip tasks')
# parser.add_argument('maximum', type=int, help='maximum simulations returned')
# parser.add_argument('id', type=str, help='simulation id')
# parser.add_argument('day', type=str, help='simulation day (only with id)')
# parser.add_argument('output_type', type=str, help='simulation output type')
# parser.add_argument('x', type=int, help='x value of point')
# parser.add_argument('y', type=int, help='y value of point')


# scenario_model = simulationsNamespace.model('Simulation', {
#     'title': fields.String(description="Scenarios title"),
#     'description': fields.String(description="Scenarios description"),
#     'userId': fields.String(description='users id'),
#     'emissions': fields.List(fields.String, description="Scenarios emissions"),
#     'date': fields.Integer(description="Scenarios date of creation"),
#     'taskId': fields.String(description="Task id"),
#     'pbpk': fields.Boolean(description="Add PBPK outputs"),
#     'pbpkDays': fields.Integer(description="Number of the pbpk simulation days")
# })

# task_model = simulationsNamespace.model('Task',{
#     '_id': fields.String(description="Tasks id"),
#     "percentage": fields.Float(description="Tasks percentage completed"),
#     "simulationKeys": fields.List(fields.String, description="Get those keys from simulation"),
#     "simulationId": fields.String(description="Simulations id"),
#     "userId": fields.String(description="User's Id"),
#     'error': fields.String(description='Error if Task completed with Error'),
#     'finishedWithError': fields.Boolean(description='Finished with error or not'),
#     'messages': fields.String(description="Simulation messages")
# })


# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if 'Authorization' in request.headers:
#             token = request.headers['Authorization']
#             token = token.split(" ")[1]
#         if not token:
#             return {'message': 'Token is missing.'}, 401
#         if oidc.validate_token(token) is True:
#             # try:
#             #     userid = oidc.user_getfield('sub', token)
#             #     qug = pyquots.get_user(userid=userid)
#             # except quotserrors.UserNotFound as unf:
#             #     quouser = pyquots_named_tuples.QuotsUser(id=userid
#             #                                           , email=oidc.user_getfield('email', token)
#             #                                           , username=oidc.user_getfield('preferred_username', token))
#             #     pyquots.create_user(quouser)
#             return f(*args, **kwargs)
#         else:
#             return {'message': 'Token is not validating.'}, 401
#     return decorated


# @simulationsNamespace.route('/', methods=['POST', 'PUT', 'GET', 'DELETE'])
# class MainClass(Resource):

#     @simulationsNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
#     # @taskNamespace.model(task_model)
#     @simulationsNamespace.param('id', 'id')
#     @simulationsNamespace.param('skip', 'skip')
#     @simulationsNamespace.param('maximum', 'maximum')
#     @simulationsNamespace.param('day', 'day')
#     @simulationsNamespace.param('output_type', 'type')
#     @simulationsNamespace.param('x', 'x')
#     @simulationsNamespace.param('y', 'y')
#     @token_required
#     # @taskNamespace.marshal_with(task_model, as_list=True)
#     def get(self,):
#         args = parser.parse_args()
#         id = args.get('id')
#         skip = args.get('skip')
#         maximum = args.get('maximum')
#         day = args.get('day')
#         output_type = args.get('output_type')
#         x = args.get('x')
#         y = args.get('y')
#         if skip is None:
#             skip = 0
#         if maximum is None:
#             maximum = 20
#         token = request.headers['Authorization']
#         token = token.split(" ")[1]
#         userid = oidc.user_getfield('sub', token)
#         if id is None:
#             query = {"userId": userid}
#             tasks_c = mongoClient['simulation'].find(query).sort([("properties.date", -1)]).skip(skip).limit(maximum)
#             total = mongoClient['simulation'].count(query)
#             simulations = []
#             for t in tasks_c:
#                 simulations.append(json_util.dumps(t))
#             resp = Response(json.dumps(simulations))
#             resp.headers["Access-Control-Expose-Headers"] = '*'
#             resp.headers["total"] = total
#             return resp
#         elif id is not None and day is None and x is None and y is None:
#             query = {"_id": id}
#             task = mongoClient['simulation'].find_one(query)
#             resp = Response(json_util.dumps(task))
#             resp.headers["Access-Control-Expose-Headers"] = '*'
#             return resp
#         elif id is not None and x is not None and y is not None:
#             query = {"simulationId": id}
#             out_all = []
#             if output_type == 'water':
#                 output = mongoClient['output_water'].find(query)
#                 for o in output:
#                     for p in o['features']:
#                         if p['properties']['x'] == x and p['properties']['y'] == y:
#                             out_all.append(p['properties'])
#                 resp = Response(json_util.dumps(out_all))
#                 resp.headers["Access-Control-Expose-Headers"] = '*'
#                 return resp
#             if output_type == 'soil':
#                 output = mongoClient['output_soil'].find(query)
#                 for o in output:
#                     for p in o['features']:
#                         if p['properties']['x'] == x and p['properties']['y'] == y:
#                             out_all.append(p['properties'])
#                 resp = Response(json_util.dumps(out_all))
#                 resp.headers["Access-Control-Expose-Headers"] = '*'
#                 return resp
#             if output_type == 'biouptake':
#                 output = mongoClient['output_biouptake'].find(query)
#                 for o in output:
#                     for p in o['features']:
#                         if p['properties']['x'] == x and p['properties']['y'] == y:
#                             out_all.append(p['properties'])
#                 resp = Response(json_util.dumps(out_all))
#                 resp.headers["Access-Control-Expose-Headers"] = '*'
#                 return resp
#             if output_type == 'sediment':
#                 output = mongoClient['output_sediment'].find(query)
#                 for o in output:
#                     for p in o['features']:
#                         if p['properties']['x'] == x and p['properties']['y'] == y:
#                             out_all.append(p['properties'])
#                 resp = Response(json_util.dumps(out_all))
#                 resp.headers["Access-Control-Expose-Headers"] = '*'
#                 return resp
#         else:
#             query = {"$and": [{"simulationId": id}, {"day": int(day)}]}
#             if output_type == 'water':
#                 output = mongoClient['output_water'].find_one(query)
#                 resp = Response(json_util.dumps(output))
#                 resp.headers["Access-Control-Expose-Headers"] = '*'
#                 return resp
#             if output_type == 'soil':
#                 output = mongoClient['output_soil'].find_one(query)
#                 resp = Response(json_util.dumps(output))
#                 resp.headers["Access-Control-Expose-Headers"] = '*'
#                 return resp
#             if output_type == 'sediment':
#                 output = mongoClient['output_sediment'].find_one(query)
#                 resp = Response(json_util.dumps(output))
#                 resp.headers["Access-Control-Expose-Headers"] = '*'
#                 return resp
#             if output_type == 'biouptake':
#                 output = mongoClient['output_biouptake'].find_one(query)
#                 resp = Response(json_util.dumps(output))
#                 resp.headers["Access-Control-Expose-Headers"] = '*'
#                 return resp

#     @simulationsNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
#     @simulationsNamespace.expect(scenario_model)
#     @simulationsNamespace.response(task_model, description="The simulations task")
#     # @imageNamespace.model(models.Image)
#     @token_required
#     def post(self):
#         token = request.headers['Authorization']
#         token = token.split(" ")[1]
#         userid = oidc.user_getfield('sub', token)
#         simulation = request.json
#         simulation['userId'] = userid
#         simId = randomString(14)
#         simulation['_id'] = simId

#         pbpkDays = int(simulation['pbpkDays'])
#         if not pbpkDays:
#             simulation['pbpkDays'] = 365
#         if int(pbpkDays) < 365:
#             pbpkDays = 365

#         task = {}
#         task['_id'] = randomString(14)
#         task['simulationId'] = simId
#         task['userId'] = userid
#         task['messages'] = ['Starting simulation']
#         task['simulationKeys'] = []
#         task['percentage'] = 0.05
#         mongoClient['task'].insert_one(task)
#         # _emission = mongoClient['prediction'].insert_one(prediction).inserted_id
#         mongoClient['simulation'].insert_one(simulation)
#         p = Process(target=run_simulation.run_simulation, args=(simulation, task, userid))
#         p.start()
#         resp = Response(json.dumps(task))
#         resp.headers["Access-Control-Expose-Headers"] = '*'
#         return resp

#     @simulationsNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
#     @simulationsNamespace.expect(scenario_model)
#     # @imageNamespace.model(models.Image)
#     @token_required
#     def put(self):
#         token = request.headers['Authorization']
#         token = token.split(" ")[1]
#         userid = oidc.user_getfield('sub', token)
#         simulation = request.json
#         myquery = {"$and": [{"userId": userid}, {"_id": simulation['id']}]}
#         update = {"$set": {"title": simulation["title"], "description": simulation["description"]}}
#         mongoClient['simulation'].update_one(myquery, update)
#         resp = Response(json.dumps(simulation))
#         resp.headers["Access-Control-Expose-Headers"] = '*'
#         return resp


# @simulationsNamespace.route('/<string:simulation_id>')
# class DeleteEmission(Resource):
#     @simulationsNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'},
#                                                      security='Bearer')
#     @simulationsNamespace.expect(scenario_model)
#     @token_required
#     def delete(self, simulation_id):
#         token = request.headers['Authorization']
#         token = token.split(" ")[1]
#         userid = oidc.user_getfield('sub', token)
#         myquery = {"$and": [{"userId": userid}, {"_id": simulation_id}]}
#         mongoClient['simulation'].delete_one(myquery)
#         myquery = {"$and": [{"userId": userid}, {"simulationId": simulation_id}]}
#         mongoClient['output_sediment'].delete_many(myquery)
#         mongoClient['output_water'].delete_many(myquery)
#         mongoClient['output_soil'].delete_many(myquery)
#         resp = Response(json.dumps({"deleted": 1}))
#         resp.headers["Access-Control-Expose-Headers"] = '*'
#         return resp


# def randomString(stringLength=10):
#     """Generate a random string of letters, digits """
#     password_characters = string.ascii_letters + string.digits + string.ascii_letters
#     return ''.join(random.choice(password_characters) for i in range(stringLength))
