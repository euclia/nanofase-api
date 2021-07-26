import re
from flask import request
from flask_restx import reqparse, fields,  Namespace, Resource
from flask import Response
from globals.globals import oidc, mongoClient
from functools import wraps
from bson import json_util
import json
import string
import random
import ast
from multiprocessing import Process
from db.region_dao import RegionDao

regionNamespace = Namespace('region')

parser = reqparse.RequestParser()
parser.add_argument('maximum', type=int, help='maximum regions returned')
parser.add_argument('id', type=str, help='region id')

EnviromentValue = regionNamespace.model('EnviromentValue',{
	'value': fields.Float(description="value"),
    'description': fields.String(description="description"),
	'unit': fields.String(description="unit"),
	'organoFate': fields.Integer(description="organoFate"),
	'ionOFate': fields.Integer(description="ionOFate"),
	'metalFate': fields.Integer(description="metalFate"),
	'nanoFate': fields.Integer(description="nanoFate")
}) 

Air = regionNamespace.model('Air',{
	'airH': fields.Nested(EnviromentValue,description="airH"),
	'airP': fields.Nested(EnviromentValue,description="airP"),
	'dynViscAir': fields.Nested(EnviromentValue,description="dynViscAir"),
	'aerP': fields.Nested(EnviromentValue,description="aerP"),
	'aerC': fields.Nested(EnviromentValue,description="aerC"),
	'radiusParticlesAer': fields.Nested(EnviromentValue,description="radiusParticlesAer"),
	'scavenging': fields.Nested(EnviromentValue,description="scavenging"),
	'scavengingENM': fields.Nested(EnviromentValue,description="scavengingENM"),
	'aerpH': fields.Nested(EnviromentValue,description="aerpH"),
	'aerOC': fields.Nested(EnviromentValue,description="aerOC")
}) 

Freshwater = regionNamespace.model('Freshwater',{
	'freshwA': fields.Nested(EnviromentValue,description="freshwA"),
	'freshwD': fields.Nested(EnviromentValue,description="freshwD"),
	'freshwP': fields.Nested(EnviromentValue,description="freshwP"),
	'freshwpH': fields.Nested(EnviromentValue,description="freshwpH"),
	'dynViscFW': fields.Nested(EnviromentValue,description="dynViscFW"),
	'freshssP': fields.Nested(EnviromentValue,description="freshssP"),
	'freshssC': fields.Nested(EnviromentValue,description="freshssC"),
	'radiusParticlesFW': fields.Nested(EnviromentValue,description="radiusParticlesFW"),
	'freshssOC': fields.Nested(EnviromentValue,description="freshssOC"),
	'sedFWD': fields.Nested(EnviromentValue,description="sedFWD"),
	'dFWSedS': fields.Nested(EnviromentValue,description="dFWSedS"),
	'fsedpercSolid': fields.Nested(EnviromentValue,description="fsedpercSolid"),
	'sedFWpH': fields.Nested(EnviromentValue,description="sedFWpH"),
	'sedFWOC': fields.Nested(EnviromentValue,description="sedFWOC"),
	'burialRateFW': fields.Nested(EnviromentValue,description="burialRateFW"),
	'resuspensionRateFW': fields.Nested(EnviromentValue,description="resuspensionRateFW"),
	'fwadvfrac': fields.Nested(EnviromentValue,description="fwadvfrac")
}) 

MarineWater = regionNamespace.model('MarineWater',{
	'seawA': fields.Nested(EnviromentValue,description="seawA"),
	'seawP': fields.Nested(EnviromentValue,description="seawP"),
	'seawD': fields.Nested(EnviromentValue,description="seawD"),
	'seawpH': fields.Nested(EnviromentValue,description="seawpH"),
	'dynViscSW': fields.Nested(EnviromentValue,description="dynViscSW"),
	'coastalA': fields.Nested(EnviromentValue,description="coastalA"),
	'seassP': fields.Nested(EnviromentValue,description="seassP"),
	'seassC': fields.Nested(EnviromentValue,description="seassC"),
	'radiusParticlesSW': fields.Nested(EnviromentValue,description="radiusParticlesSW"),
	'seassOC': fields.Nested(EnviromentValue,description="seassOC"),
	'sedSWD': fields.Nested(EnviromentValue,description="sedSWD"),
	'dSWSedS': fields.Nested(EnviromentValue,description="dSWSedS"),
	'ssedpercSolid': fields.Nested(EnviromentValue,description="ssedpercSolid"),
	'sedSWpH': fields.Nested(EnviromentValue,description="sedSWpH"),
	'sedSWOC': fields.Nested(EnviromentValue,description="sedSWOC"),
	'burialRateSW': fields.Nested(EnviromentValue,description="burialRateSW"),
	'resuspensionRateSW': fields.Nested(EnviromentValue,description="resuspensionRateSW"),
	'swadvfrac': fields.Nested(EnviromentValue,description="swadvfrac")
}) 

SoilSite1 = regionNamespace.model('SoilSite1',{
	'soilS1': fields.String(description="soilS1"),
	'soilA1': fields.Nested(EnviromentValue,description="soilA1"),
	'CEC_S1': fields.Nested(EnviromentValue,description="CEC_S1"),
	'metal_S1': fields.Nested(EnviromentValue,description="metal_S1"),
	'soilD1': fields.Nested(EnviromentValue,description="soilD1"),
	'dSS1': fields.Nested(EnviromentValue,description="dSS1"),
	'soilWC1': fields.Nested(EnviromentValue,description="soilWC1"),
	'soilWpH1': fields.Nested(EnviromentValue,description="soilWpH1"),
	'soilAC1': fields.Nested(EnviromentValue,description="soilAC1"),
	'soilOC1': fields.Nested(EnviromentValue,description="soilOC1"),
	'CN1': fields.Nested(EnviromentValue,description="CN1"),
	'FC1': fields.Nested(EnviromentValue,description="FC1"),
	'deepsD1': fields.Nested(EnviromentValue,description="deepsD1"),
	'CEC_deepS1': fields.Nested(EnviromentValue,description="CEC_deepS1"),
	'metal_deepS1': fields.Nested(EnviromentValue,description="metal_deepS1"),
	'deepsP1': fields.Nested(EnviromentValue,description="deepsP1"),
	'dsoilOC1': fields.Nested(EnviromentValue,description="dsoilOC1"),
	'A1': fields.Nested(EnviromentValue,description="A1"),
	'TSV1': fields.Nested(EnviromentValue,description="TSV1"),
	'TSVmin1': fields.Nested(EnviromentValue,description="TSVmin1"),
	'z_wind1': fields.Nested(EnviromentValue,description="z_wind1"),
	'roughness1': fields.Nested(EnviromentValue,description="roughness1"),
	'Kconstant1': fields.Nested(EnviromentValue,description="Kconstant1"),
	'percWind1': fields.Nested(EnviromentValue,description="percWind1"),
	'windConstant1': fields.Nested(EnviromentValue,description="windConstant1"),
	'percUncovered1': fields.Nested(EnviromentValue,description="percUncovered1"),
	'percSuspended1': fields.Nested(EnviromentValue,description="percSuspended1"),
	'Kfact1': fields.Nested(EnviromentValue,description="Kfact1"),
	'slope1': fields.Nested(EnviromentValue,description="slope1"),
	'cropManageFactor1': fields.Nested(EnviromentValue,description="cropManageFactor1"),
	'supportFactor1': fields.Nested(EnviromentValue,description="supportFactor1"),
	'leachingR1': fields.Nested(EnviromentValue,description="leachingR1")
}) 

SoilSite2 = regionNamespace.model('SoilSite2',{
	'soilS2': fields.String(description="soilS2"),
	'soilA2': fields.Nested(EnviromentValue,description="soilA2"),
	'CEC_S2': fields.Nested(EnviromentValue,description="CEC_S2"),
	'metal_S2': fields.Nested(EnviromentValue,description="metal_S2"),
	'soilD2': fields.Nested(EnviromentValue,description="soilD2"),
	'dSS2': fields.Nested(EnviromentValue,description="dSS2"),
	'soilWC2': fields.Nested(EnviromentValue,description="soilWC2"),
	'soilWpH2': fields.Nested(EnviromentValue,description="soilWpH2"),
	'soilAC2': fields.Nested(EnviromentValue,description="soilAC2"),
	'soilOC2': fields.Nested(EnviromentValue,description="soilOC2"),
	'CN2': fields.Nested(EnviromentValue,description="CN2"),
	'FC2': fields.Nested(EnviromentValue,description="FC2"),
	'deepsD2': fields.Nested(EnviromentValue,description="deepsD2"),
	'CEC_deepS2': fields.Nested(EnviromentValue,description="CEC_deepS2"),
	'metal_deepS2': fields.Nested(EnviromentValue,description="metal_deepS2"),
	'deepsP2': fields.Nested(EnviromentValue,description="deepsP2"),
	'dsoilOC2': fields.Nested(EnviromentValue,description="dsoilOC2"),
	'A2': fields.Nested(EnviromentValue,description="A2"),
	'TSV2': fields.Nested(EnviromentValue,description="TSV2"),
	'TSVmin2': fields.Nested(EnviromentValue,description="TSVmin2"),
	'z_wind2': fields.Nested(EnviromentValue,description="z_wind2"),
	'roughness2': fields.Nested(EnviromentValue,description="roughness2"),
	'Kconstant2': fields.Nested(EnviromentValue,description="Kconstant2"),
	'percWind2': fields.Nested(EnviromentValue,description="percWind2"),
	'windConstant2': fields.Nested(EnviromentValue,description="windConstant2"),
	'percUncovered2': fields.Nested(EnviromentValue,description="percUncovered2"),
	'percSuspended2': fields.Nested(EnviromentValue,description="percSuspended2"),
	'Kfact2': fields.Nested(EnviromentValue,description="Kfact2"),
	'slope2': fields.Nested(EnviromentValue,description="slope2"),
	'cropManageFactor2': fields.Nested(EnviromentValue,description="cropManageFactor2"),
	'supportFactor2': fields.Nested(EnviromentValue,description="supportFactor2"),
	'leachingR2': fields.Nested(EnviromentValue,description="leachingR2")
}) 

SoilSite3 = regionNamespace.model('SoilSite3',{
	'soilS3': fields.String(description="soilS3"),
	'soilA3': fields.Nested(EnviromentValue,description="soilA3"),
	'CEC_S3': fields.Nested(EnviromentValue,description="CEC_S3"),
	'metal_S3': fields.Nested(EnviromentValue,description="metal_S3"),
	'soilD3': fields.Nested(EnviromentValue,description="soilD3"),
	'dSS3': fields.Nested(EnviromentValue,description="dSS3"),
	'soilWC3': fields.Nested(EnviromentValue,description="soilWC3"),
	'soilWpH3': fields.Nested(EnviromentValue,description="soilWpH3"),
	'soilAC3': fields.Nested(EnviromentValue,description="soilAC3"),
	'soilOC3': fields.Nested(EnviromentValue,description="soilOC3"),
	'CN3': fields.Nested(EnviromentValue,description="CN3"),
	'FC3': fields.Nested(EnviromentValue,description="FC3"),
	'deepsD3': fields.Nested(EnviromentValue,description="deepsD3"),
	'CEC_deepS3': fields.Nested(EnviromentValue,description="CEC_deepS3"),
	'metal_deepS3': fields.Nested(EnviromentValue,description="metal_deepS3"),
	'deepsP3': fields.Nested(EnviromentValue,description="deepsP3"),
	'dsoilOC3': fields.Nested(EnviromentValue,description="dsoilOC3"),
	'A3': fields.Nested(EnviromentValue,description="A3"),
	'TSV3': fields.Nested(EnviromentValue,description="TSV3"),
	'TSVmin3': fields.Nested(EnviromentValue,description="TSVmin3"),
	'z_wind3': fields.Nested(EnviromentValue,description="z_wind3"),
	'roughness3': fields.Nested(EnviromentValue,description="roughness3"),
	'Kconstant3': fields.Nested(EnviromentValue,description="Kconstant3"),
	'percWind3': fields.Nested(EnviromentValue,description="percWind3"),
	'windConstant3': fields.Nested(EnviromentValue,description="windConstant3"),
	'percUncovered3': fields.Nested(EnviromentValue,description="percUncovered3"),
	'percSuspended3': fields.Nested(EnviromentValue,description="percSuspended3"),
	'Kfact3': fields.Nested(EnviromentValue,description="Kfact3"),
	'slope3': fields.Nested(EnviromentValue,description="slope3"),
	'cropManageFactor3': fields.Nested(EnviromentValue,description="cropManageFactor3"),
	'supportFactor3': fields.Nested(EnviromentValue,description="supportFactor3"),
	'leachingR3': fields.Nested(EnviromentValue,description="leachingR3")
}) 

SoilSite4 = regionNamespace.model('SoilSite4',{
	'soilS4': fields.String(description="soilS4"),
	'soilA4': fields.Nested(EnviromentValue,description="soilA4"),
	'CEC_S4': fields.Nested(EnviromentValue,description="CEC_S4"),
	'metal_S4': fields.Nested(EnviromentValue,description="metal_S4"),
	'soilD4': fields.Nested(EnviromentValue,description="soilD4"),
	'dSS4': fields.Nested(EnviromentValue,description="dSS4"),
	'soilWC4': fields.Nested(EnviromentValue,description="soilWC4"),
	'soilWpH4': fields.Nested(EnviromentValue,description="soilWpH4"),
	'soilAC4': fields.Nested(EnviromentValue,description="soilAC4"),
	'soilOC4': fields.Nested(EnviromentValue,description="soilOC4"),
	'CN4': fields.Nested(EnviromentValue,description="CN4"),
	'FC4': fields.Nested(EnviromentValue,description="FC4"),
	'deepsD4': fields.Nested(EnviromentValue,description="deepsD4"),
	'CEC_deepS4': fields.Nested(EnviromentValue,description="CEC_deepS4"),
	'metal_deepS4': fields.Nested(EnviromentValue,description="metal_deepS4"),
	'deepsP4': fields.Nested(EnviromentValue,description="deepsP4"),
	'dsoilOC4': fields.Nested(EnviromentValue,description="dsoilOC4"),
	'A4': fields.Nested(EnviromentValue,description="A4"),
	'TSV4': fields.Nested(EnviromentValue,description="TSV4"),
	'TSVmin4': fields.Nested(EnviromentValue,description="TSVmin4"),
	'z_wind4': fields.Nested(EnviromentValue,description="z_wind4"),
	'roughness4': fields.Nested(EnviromentValue,description="roughness4"),
	'Kconstant4': fields.Nested(EnviromentValue,description="Kconstant4"),
	'percWind4': fields.Nested(EnviromentValue,description="percWind4"),
	'windConstant4': fields.Nested(EnviromentValue,description="windConstant4"),
	'percUncovered4': fields.Nested(EnviromentValue,description="percUncovered4"),
	'percSuspended4': fields.Nested(EnviromentValue,description="percSuspended4"),
	'Kfact4': fields.Nested(EnviromentValue,description="Kfact4"),
	'slope4': fields.Nested(EnviromentValue,description="slope4"),
	'cropManageFactor4': fields.Nested(EnviromentValue,description="cropManageFactor4"),
	'supportFactor4': fields.Nested(EnviromentValue,description="supportFactor4"),
	'leachingR4': fields.Nested(EnviromentValue,description="leachingR4")
}) 

EnviromentRegion = regionNamespace.model('EnviromentRegion',{
	'name': fields.String(description="name"),
	'air': fields.Nested(Air,description="air"),
	'fw': fields.Nested(Freshwater,description="fw"),
	'sw': fields.Nested(MarineWater,description="sw"),
	'soil1': fields.Nested(SoilSite1,description="soil1"),
	'soil2': fields.Nested(SoilSite2,description="soil2"),
	'soil3': fields.Nested(SoilSite3,description="soil3"),
	'soil4': fields.Nested(SoilSite4,description="soil4")
}) 

PresenceRegion = regionNamespace.model('PresenceRegion',{
	'air': fields.Integer(description="air"),
	'fw': fields.Integer(description="fw"),
	'sw': fields.Integer(description="sw"),
	'soil1': fields.Integer(description="soil1"),
	'soil2': fields.Integer(description="soil2"),
	'soil3': fields.Integer(description="soil3"),
	'soil4': fields.Integer(description="soil4")
}) 

ClimateRegion = regionNamespace.model('ClimateRegion',{
	'month': fields.List(fields.Integer, description="month"),
	'day': fields.List(fields.Integer, description="day"),
	'year': fields.List(fields.Integer, description="year"),
	'precipitation': fields.List(fields.Float, description="precipitation"),
	'windspeeed': fields.List(fields.Float, description="windspeeed"),
	'waterflow': fields.List(fields.Float, description="waterflow"),
	'temperature': fields.List(fields.Float, description="temperature"),
	'evaporation': fields.List(fields.Float, description="evaporation")
}) 

Region = regionNamespace.model('Region',{
    '_id': fields.String(description="Document ID"),
    'userId': fields.String(description="User's ID"),
	'Enviroment': fields.Nested(EnviromentRegion,description="Enviroment"),
	'Presence': fields.Nested(PresenceRegion,description="Presence"),
	'Climate': fields.Nested(ClimateRegion,description="Climate")
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
            return f(*args, **kwargs)
        else:
            return {'message': 'Token is not validating.'}, 401
    return decorated


@regionNamespace.route('/', methods=['POST', 'PUT', 'GET', 'DELETE'])
class MainClass(Resource):

    region_dao = RegionDao(mongoClient=mongoClient)

    @regionNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @regionNamespace.param('id', 'id')
    @regionNamespace.param('maximum', 'maximum')
    @token_required
    def get(self,):
        args = parser.parse_args()
        id = args.get('id')
        maximum = args.get('maximum')
       
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        if id is None:
            region_q, total = self.region_dao.find({'userId': userid, 'maximum': maximum})
            regions = []
            for r in region_q:
                regions.append(json_util.dumps(r))
            resp = Response(json.dumps(regions))
            resp.headers["Access-Control-Expose-Headers"] = '*'
            resp.headers["total"] = total
            return resp
        else:
            region_q = self.region_dao.find_one({'userId': userid, '_id': id})
            resp = Response(json_util.dumps(region_q))
            resp.headers["Access-Control-Expose-Headers"] = '*'
            return resp

    @regionNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @regionNamespace.expect(Region)
    @token_required
    def post(self):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        region: Region = request.json
        region['userId'] = userid
        simId = randomString(14)
        region['_id'] = simId

        self.region_dao.insert_one(region)
        
        resp = Response(json.dumps(region))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp


    @regionNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @regionNamespace.expect(Region)
    @regionNamespace.response(fields.String, description="The region of the simulation")
    @token_required
    def put(self):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        region: Region = request.json
        
        print('JASON')
        query = {"userId": userid, '_id': region['_id']}
        reg = self.region_dao.update_one(query, region)
        
        resp = Response(json.dumps(reg))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp

@regionNamespace.route('/<string:region_id>')
class DeleteEmission(Resource):

    region_dao = RegionDao(mongoClient=mongoClient)

    @regionNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'},
                                                     security='Bearer')
    @token_required
    def delete(self, region_id):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        
        region_id = self.region_dao.delete_one(userid, region_id)

        resp = Response(json.dumps({"deleted": 1}))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp

def randomString(stringLength=10):
    """Generate a random string of letters, digits """
    password_characters = string.ascii_letters + string.digits + string.ascii_letters
    return ''.join(random.choice(password_characters) for i in range(stringLength))
