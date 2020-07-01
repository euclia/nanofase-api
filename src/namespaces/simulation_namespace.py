from flask import request
from flask_restx import reqparse, fields,  Namespace, Resource
from flask import Response
from src.globals.globals import oidc, mongoClient
from src.simulation import run_simulation
from functools import wraps
from bson import json_util
import json
import string
import random
from multiprocessing import Process


simulationsNamespace = Namespace('simulation')

parser = reqparse.RequestParser()
parser.add_argument('skip', type=int, help='skip tasks')
parser.add_argument('maximum', type=int, help='maximum tasks returned')
parser.add_argument('id', type=str, help='task id')


scenario_model = simulationsNamespace.model('Simulation', {
    'title': fields.String(description="Scenarios title"),
    'description': fields.String(description="Scenarios description"),
    'userId': fields.String(description='users id'),
    'emissions': fields.List(fields.String, description="Scenarios emissions"),
    'date': fields.Integer(description="Scenarios date of creation"),
    'taskId': fields.String(description="Task id")
})


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            token = token.split(" ")[1]
        if not token:
            return {'message': 'Token is missing.'}, 401
        if oidc.validate_token(token) is True:
            # try:
            #     userid = oidc.user_getfield('sub', token)
            #     qug = pyquots.get_user(userid=userid)
            # except quotserrors.UserNotFound as unf:
            #     quouser = pyquots_named_tuples.QuotsUser(id=userid
            #                                           , email=oidc.user_getfield('email', token)
            #                                           , username=oidc.user_getfield('preferred_username', token))
            #     pyquots.create_user(quouser)
            return f(*args, **kwargs)
        else:
            return {'message': 'Token is not validating.'}, 401
    return decorated


@simulationsNamespace.route('/', methods=['POST', 'PUT', 'GET', 'DELETE'])
class MainClass(Resource):

    @simulationsNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    # @taskNamespace.model(task_model)
    @simulationsNamespace.param('id', 'id')
    @simulationsNamespace.param('skip', 'skip')
    @simulationsNamespace.param('maximum', 'maximum')
    @token_required
    # @taskNamespace.marshal_with(task_model, as_list=True)
    def get(self,):
        args = parser.parse_args()
        id = args.get('id')
        skip = args.get('skip')
        maximum = args.get('maximum')
        if skip is None:
            skip = 0
        if maximum is None:
            maximum = 20
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        if id is None:
            query = {"userId": userid}
            tasks_c = mongoClient['simulation'].find(query).sort([("properties.date", -1)]).skip(skip).limit(maximum)
            total = mongoClient['simulation'].count(query)
            emmisions = []
            for t in tasks_c:
                emmisions.append(json_util.dumps(t))
            resp = Response(json.dumps(emmisions))
            resp.headers["Access-Control-Expose-Headers"] = '*'
            resp.headers["total"] = total
            return resp
        else:
            query = {"_id": id}
            task = mongoClient['simulation'].find_one(query)
            resp = Response(json_util.dumps(task))
            resp.headers["Access-Control-Expose-Headers"] = '*'
            return resp

    @simulationsNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @simulationsNamespace.expect(scenario_model)
    # @imageNamespace.model(models.Image)
    @token_required
    def post(self):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        simulation = request.json
        simulation['userId'] = userid
        simulation['_id'] = randomString(14)
        # _emission = mongoClient['prediction'].insert_one(prediction).inserted_id
        mongoClient['simulation'].insert_one(simulation)
        p = Process(target=run_simulation.run_simulation, args=(simulation, None))
        p.start()
        resp = Response(json.dumps(simulation))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp

    @simulationsNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @simulationsNamespace.expect(scenario_model)
    # @imageNamespace.model(models.Image)
    @token_required
    def put(self):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        simulation = request.json
        myquery = {"$and": [{"userId": userid}, {"_id": simulation['id']}]}
        update = {"$set": {"emissions":  simulation['emissions'], "title": simulation["title"], "description": simulation["description"]}}
        mongoClient['scenario'].update_one(myquery, update)
        resp = Response(json.dumps(simulation))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp


@simulationsNamespace.route('/<string:simulation_id>')
class DeleteEmission(Resource):
    @simulationsNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'},
                                                     security='Bearer')
    @simulationsNamespace.expect(scenario_model)
    @token_required
    def delete(self, scenario_id):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        myquery = {"$and": [{"userId": userid}, {"_id": scenario_id}]}
        mongoClient['simulation'].delete_one(myquery)
        resp = Response(json.dumps({"deleted": 1}))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp


def randomString(stringLength=10):
    """Generate a random string of letters, digits """
    password_characters = string.ascii_letters + string.digits + string.ascii_letters + "@#$!>?"
    return ''.join(random.choice(password_characters) for i in range(stringLength))
