from flask import request
from flask_restx  import reqparse, fields,  Namespace, Resource
from flask import Response
from src.globals.globals import oidc, mongoClient
from functools import wraps
from bson import json_util, ObjectId
import json


emissionNamespace = Namespace('emission')

parser = reqparse.RequestParser()
parser.add_argument('skip', type=int, help='skip tasks')
parser.add_argument('maximum', type=int, help='maximum tasks returned')
parser.add_argument('id', type=str, help='task id')

properties = emissionNamespace.model('Properties',{
    'title': fields.String(description="Emissions title"),
    'date': fields.Integer(description="Emissions creation date"),
    'description': fields.Integer(description="Emissions description"),
    'nanomaterial': fields.String(description="Emissions nanomaterial"),
    'compartment': fields.String(description="Emissions compartment"),
    'form': fields.String(description="form"),
    'temporalProfile': fields.String(description="temporalProfile"),
    'saved': fields.Boolean(description="Saved or not on database")
})

geometry = emissionNamespace.model('Geometry',{
    'coordinates': fields.Arbitrary(description="Emissions coordinates"),
    'type': fields.String(description="Geometry type"),
})

emission_model = emissionNamespace.model('Emission', {
    'id': fields.String(description="Emissions ID"),
    'properties': fields.Nested(properties, description="Emissions properties"),
    'userId': fields.String(description='users id'),
    'geometry': fields.Nested(geometry, description="Emissions properties"),
    'type': fields.String(description="Mapbox type")
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


@emissionNamespace.route('/', methods=['POST', 'PUT', 'GET', 'DELETE'])
class MainClass(Resource):

    @emissionNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    # @taskNamespace.model(task_model)
    @emissionNamespace.param('id', 'id')
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
            tasks_c = mongoClient['emission'].find(query).skip(skip).limit(maximum)
            total = mongoClient['emission'].count(query)
            tasks = []
            for t in tasks_c:
                tasks.append(json_util.dumps(t))
            resp = Response(tasks)
            resp.headers["Access-Control-Expose-Headers"] = '*'
            resp.headers["Access-Control-Expose-Headers"] = total
            return resp
        else:
            query = {"_id": id}
            task = mongoClient['emission'].find_one(query)
            resp = Response(json_util.dumps(task))
            resp.headers["Access-Control-Expose-Headers"] = '*'
            return resp

    @emissionNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @emissionNamespace.expect(emission_model)
    # @imageNamespace.model(models.Image)
    @token_required
    def post(self):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        emission = request.json
        emission['userId'] = userid
        emission['_id'] = emission['id']
        emission['properties']['saved'] = True
        # _emission = mongoClient['prediction'].insert_one(prediction).inserted_id
        mongoClient['emission'].insert_one(emission)
        resp = Response(json.dumps(emission))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp

    @emissionNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @emissionNamespace.expect(emission_model)
    # @imageNamespace.model(models.Image)
    @token_required
    def put(self):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        emission = request.json
        myquery = {"$and": [{"userId": userid}, {"_id": emission['id']}]}
        update = {"$set": {"geometry":  emission['geometry'], "properties": emission["properties"]}}
        mongoClient['emission'].update_one(myquery, update)
        resp = Response(json.dumps(emission))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp



@emissionNamespace.route('/<string:emission_id>')
class DeleteEmission(Resource):
    @emissionNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'},
                                                     security='Bearer')
    @emissionNamespace.expect(emission_model)
    @token_required
    def delete(self, emission_id):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        myquery = {"$and": [{"userId": userid}, {"_id": emission_id}]}
        mongoClient['emission'].delete_one(myquery)
        resp = Response({"deleted": 1})
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp