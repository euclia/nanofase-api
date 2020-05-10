from flask import request
from flask_restx  import reqparse, fields,  Namespace, Resource
from flask import Response
from src.globals.globals import oidc, mongoClient
from functools import wraps
from bson import json_util, ObjectId
import json
import string
import random


scenariosNamespace = Namespace('scenario')

parser = reqparse.RequestParser()
parser.add_argument('skip', type=int, help='skip tasks')
parser.add_argument('maximum', type=int, help='maximum tasks returned')
parser.add_argument('id', type=str, help='task id')


scenario_model = scenariosNamespace.model('Scenario', {
    'title': fields.String(description="Scenarios title"),
    'description': fields.String(description="Scenarios description"),
    'userId': fields.String(description='users id'),
    'emissions': fields.List(fields.String,description="Scenarios emissions"),
    'date': fields.Integer(description="Scenarios date of creation")
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


@scenariosNamespace.route('/', methods=['POST', 'PUT', 'GET', 'DELETE'])
class MainClass(Resource):

    @scenariosNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    # @taskNamespace.model(task_model)
    @scenariosNamespace.param('id', 'id')
    @scenariosNamespace.param('skip', 'skip')
    @scenariosNamespace.param('maximum', 'maximum')
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
            tasks_c = mongoClient['scenario'].find(query).sort([( "properties.date" , -1)]).skip(skip).limit(maximum)
            total = mongoClient['scenario'].count(query)
            emmisions = []
            for t in tasks_c:
                emmisions.append(json_util.dumps(t))
            resp = Response(json.dumps(emmisions))
            resp.headers["Access-Control-Expose-Headers"] = '*'
            resp.headers["Access-Control-Expose-Headers"] = total
            return resp
        else:
            query = {"_id": id}
            task = mongoClient['scenario'].find_one(query)
            resp = Response(json_util.dumps(task))
            resp.headers["Access-Control-Expose-Headers"] = '*'
            return resp

    @scenariosNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @scenariosNamespace.expect(scenario_model)
    # @imageNamespace.model(models.Image)
    @token_required
    def post(self):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        scenario = request.json
        scenario['userId'] = userid
        scenario['_id'] = randomString(14)
        # _emission = mongoClient['prediction'].insert_one(prediction).inserted_id
        mongoClient['scenario'].insert_one(scenario)
        resp = Response(json.dumps(scenario))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp

    @scenariosNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @scenariosNamespace.expect(scenario_model)
    # @imageNamespace.model(models.Image)
    @token_required
    def put(self):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        scenario = request.json
        myquery = {"$and": [{"userId": userid}, {"_id": scenario['id']}]}
        update = {"$set": {"emissions":  scenario['emissions'], "title": scenario["title"], "description": scenario["description"]}}
        mongoClient['scenario'].update_one(myquery, update)
        resp = Response(json.dumps(scenario))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp



@scenariosNamespace.route('/<string:scenario_id>')
class DeleteEmission(Resource):
    @scenariosNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'},
                                                     security='Bearer')
    @scenariosNamespace.expect(scenario_model)
    @token_required
    def delete(self, scenario_id):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        myquery = {"$and": [{"userId": userid}, {"_id": scenario_id}]}
        mongoClient['scenario'].delete_one(myquery)
        resp = Response(json.dumps({"deleted": 1}))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp


def randomString(stringLength=10):
    """Generate a random string of letters, digits """
    password_characters = string.ascii_letters + string.digits + string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(stringLength))