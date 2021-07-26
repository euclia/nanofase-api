from flask import request
from flask_restx import reqparse, fields,  Namespace, Resource
from flask import Response
from globals.globals import oidc, mongoClient
from functools import wraps
from bson import json_util
import json
import string
import random
from db.enm_dao import ENMDao
import enum

enmNamespace = Namespace('ENM')


# Using enum class create enumerations
class Materials(enum.Enum):
    nonIon = 'nonIon'
    ion = 'ion'
    nanomaterial = 'nanomaterial'
    metal = 'metal'


parser = reqparse.RequestParser()
parser.add_argument('maximum', type=int, help='maximum enms returned')
parser.add_argument('id', type=str, help='enm id')
parser.add_argument('material', type=Materials, help='Material flag')


NonIonizableParams = enmNamespace.model('NonIonizableParams', {
    'name': fields.String(description="name"),
    'MW': fields.Float(description="MW"),
    'MD': fields.Float(description="MD"),
    'Kow_n': fields.Float(description="Kow_n"),
    'Koc_n': fields.Float(description="Koc_n"),
    'Kaw_n': fields.Float(description="Kaw_n"),
    'Kp_n': fields.Float(description="Kp_n"),
    'HL_air_n': fields.Float(description="HL_air_n"),
    'HL_aer_n': fields.Float(description="HL_aer_n"),
    'HL_fWater_n': fields.Float(description="HL_fWater_n"),
    'HL_fSS_n': fields.Float(description="HL_fSS_n"),
    'HL_fSedW_n': fields.Float(description="HL_fSedW_n"),
    'HL_fSedS_n': fields.Float(description="HL_fSedS_n"),
    'HL_sWater_n': fields.Float(description="HL_sWater_n"),
    'HL_sSS_n': fields.Float(description="HL_sSS_n"),
    'HL_sSedW_n': fields.Float(description="HL_sSedW_n"),
    'HL_sSedS_n': fields.Float(description="HL_sSedS_n"),
    'HL_soilA1_n': fields.Float(description="HL_soilA1_n"),
    'HL_soilW1_n': fields.Float(description="HL_soilW1_n"),
    'HL_soilS1_n': fields.Float(description="HL_soilS1_n"),
    'HL_soilDeep1_n': fields.Float(description="HL_soilDeep1_n"),
    'HL_soilA2_n': fields.Float(description="HL_soilA2_n"),
    'HL_soilW2_n': fields.Float(description="HL_soilW2_n"),
    'HL_soilS2_n': fields.Float(description="HL_soilS2_n"),
    'HL_soilDeep2_n': fields.Float(description="HL_soilDeep2_n"),
    'HL_soilA3_n': fields.Float(description="HL_soilA3_n"),
    'HL_soilW3_n': fields.Float(description="HL_soilW3_n"),
    'HL_soilS3_n': fields.Float(description="HL_soilS3_n"),
    'HL_soilDeep3_n': fields.Float(description="HL_soilDeep3_n"),
    'HL_soilA4_n': fields.Float(description="HL_soilA4_n"),
    'HL_soilW4_n': fields.Float(description="HL_soilW4_n"),
    'HL_soilS4_n': fields.Float(description="HL_soilS4_n"),
    'HL_soilDeep4_n': fields.Float(description="HL_soilDeep4_n")
})

IonizableParams = enmNamespace.model('IonizableParams', {
    'name': fields.String(description="name"),
    'smiles': fields.String(description="smiles"),
    'cas': fields.String(description="cas"),
    'type': fields.String(description="type"),
    'pKa': fields.Float(description="pKa"),
    'MW': fields.Float(description="MW"),
    'Koa_n': fields.Float(description="Koa_n"),
    'Kow_n': fields.Float(description="Kow_n"),
    'Koc_n': fields.Float(description="Koc_n"),
    'Kaw_n': fields.Float(description="Kaw_n"),
    'Kp_n': fields.Float(description="Kp_n"),
    'enrichFactor': fields.Float(description="enrichFactor"),
    'HL_air_n': fields.Float(description="HL_air_n"),
    'HL_aer_n': fields.Float(description="HL_aer_n"),
    'HL_aer_i': fields.Float(description="HL_aer_i"),
    'HL_fWater_n': fields.Float(description="HL_fWater_n"),
    'HL_fWater_i': fields.Float(description="HL_fWater_i"),
    'HL_fSS_n': fields.Float(description="HL_fSS_n"),
    'HL_fSS_i': fields.Float(description="HL_fSS_i"),
    'HL_fSedW_n': fields.Float(description="HL_fSedW_n"),
    'HL_fSedW_i': fields.Float(description="HL_fSedW_i"),
    'HL_fSedS_n': fields.Float(description="HL_fSedS_n"),
    'HL_fSedS_i': fields.Float(description="HL_fSedS_i"),
    'HL_sWater_n': fields.Float(description="HL_sWater_n"),
    'HL_sWater_i': fields.Float(description="HL_sWater_i"),
    'HL_sSS_n': fields.Float(description="HL_sSS_n"),
    'HL_sSS_i': fields.Float(description="HL_sSS_i"),
    'HL_sSedW_n': fields.Float(description="HL_sSedW_n"),
    'HL_sSedW_i': fields.Float(description="HL_sSedW_i"),
    'HL_sSedS_n': fields.Float(description="HL_sSedS_n"),
    'HL_sSedS_i': fields.Float(description="HL_sSedS_i"),
    'HL_soilA1_n': fields.Float(description="HL_soilA1_n"),
    'HL_soilA1_i': fields.Float(description="HL_soilA1_i"),
    'HL_soilW1_n': fields.Float(description="HL_soilW1_n"),
    'HL_soilW1_i': fields.Float(description="HL_soilW1_i"),
    'HL_soilS1_n': fields.Float(description="HL_soilS1_n"),
    'HL_soilS1_i': fields.Float(description="HL_soilS1_i"),
    'HL_soilDeep1_n': fields.Float(description="HL_soilDeep1_n"),
    'HL_soilDeep1_i': fields.Float(description="HL_soilDeep1_i"),
    'HL_soilA2_n': fields.Float(description="HL_soilA2_n"),
    'HL_soilA2_i': fields.Float(description="HL_soilA2_i"),
    'HL_soilW2_n': fields.Float(description="HL_soilW2_n"),
    'HL_soilW2_i': fields.Float(description="HL_soilW2_i"),
    'HL_soilS2_n': fields.Float(description="HL_soilS2_n"),
    'HL_soilS2_i': fields.Float(description="HL_soilS2_i"),
    'HL_soilDeep2_n': fields.Float(description="HL_soilDeep2_n"),
    'HL_soilDeep2_i': fields.Float(description="HL_soilDeep2_i"),
    'HL_soilA3_n': fields.Float(description="HL_soilA3_n"),
    'HL_soilA3_i': fields.Float(description="HL_soilA3_i"),
    'HL_soilW3_n': fields.Float(description="HL_soilW3_n"),
    'HL_soilW3_i': fields.Float(description="HL_soilW3_i"),
    'HL_soilS3_n': fields.Float(description="HL_soilS3_n"),
    'HL_soilS3_i': fields.Float(description="HL_soilS3_i"),
    'HL_soilDeep3_n': fields.Float(description="HL_soilDeep3_n"),
    'HL_soilDeep3_i': fields.Float(description="HL_soilDeep3_i"),
    'HL_soilA4_n': fields.Float(description="HL_soilA4_n"),
    'HL_soilA4_i': fields.Float(description="HL_soilA4_i"),
    'HL_soilW4_n': fields.Float(description="HL_soilW4_n"),
    'HL_soilW4_i': fields.Float(description="HL_soilW4_i"),
    'HL_soilS4_n': fields.Float(description="HL_soilS4_n"),
    'HL_soilS4_i': fields.Float(description="HL_soilS4_i"),
    'HL_soilDeep4_n': fields.Float(description="HL_soilDeep4_n"),
    'HL_soilDeep4_i': fields.Float(description="HL_soilDeep4_i"),
    'Fr_air_n': fields.Float(description="Fr_air_n"),
    'Fr_air_i': fields.Float(description="Fr_air_i"),
    'Fr_fw_n': fields.Float(description="Fr_fw_n"),
    'Fr_fw_i': fields.Float(description="Fr_fw_i"),
    'Fr_fwSed_n': fields.Float(description="Fr_fwSed_n"),
    'Fr_fwSed_i': fields.Float(description="Fr_fwSed_i"),
    'Fr_sw_n': fields.Float(description="Fr_sw_n"),
    'Fr_sw_i': fields.Float(description="Fr_sw_i"),
    'Fr_swSed_n': fields.Float(description="Fr_swSed_n"),
    'Fr_swSed_i': fields.Float(description="Fr_swSed_i"),
    'Fr_soil1_n': fields.Float(description="Fr_soil1_n"),
    'Fr_soil1_i': fields.Float(description="Fr_soil1_i"),
    'Fr_deepS1_n': fields.Float(description="Fr_deepS1_n"),
    'Fr_deepS1_i': fields.Float(description="Fr_deepS1_i"),
    'Fr_soil2_n': fields.Float(description="Fr_soil2_n"),
    'Fr_soil2_i': fields.Float(description="Fr_soil2_i"),
    'Fr_deepS2_n': fields.Float(description="Fr_deepS2_n"),
    'Fr_deepS2_i': fields.Float(description="Fr_deepS2_i"),
    'Fr_soil3_n': fields.Float(description="Fr_soil3_n"),
    'Fr_soil3_i': fields.Float(description="Fr_soil3_i"),
    'Fr_deepS3_n': fields.Float(description="Fr_deepS3_n"),
    'Fr_deepS3_i': fields.Float(description="Fr_deepS3_i"),
    'Fr_soil4_n': fields.Float(description="Fr_soil4_n"),
    'Fr_soil4_i': fields.Float(description="Fr_soil4_i"),
    'Fr_deepS4_n': fields.Float(description="Fr_deepS4_n"),
    'Fr_deepS4_i': fields.Float(description="Fr_deepS4_i"),
    'Kd_air_i': fields.Float(description="Kd_air_i"),
    'Kd_fw_i': fields.Float(description="Kd_fw_i"),
    'Kd_fwSed_i': fields.Float(description="Kd_fwSed_i"),
    'Kd_sw_i': fields.Float(description="Kd_sw_i"),
    'Kd_swSed_i': fields.Float(description="Kd_swSed_i"),
    'Kd_soil1_i': fields.Float(description="Kd_soil1_i"),
    'Kd_deepS1_i': fields.Float(description="Kd_deepS1_i"),
    'Kd_soil2_i': fields.Float(description="Kd_soil2_i"),
    'Kd_deepS2_i': fields.Float(description="Kd_deepS2_i"),
    'Kd_soil3_i': fields.Float(description="Kd_soil3_i"),
    'Kd_deepS3_i': fields.Float(description="Kd_deepS3_i"),
    'Kd_soil4_i': fields.Float(description="Kd_soil4_i"),
    'Kd_deepS4_i': fields.Float(description="Kd_deepS4_i")
})

NanomaterialParams = enmNamespace.model('NanomaterialParams', {
    'name': fields.String(description="name"),
    'ENM': fields.String(description="ENM"),
    'diameter': fields.Float(description="diameter"),
    'radiusENMagg': fields.Float(description="radiusENMagg"),
    'density': fields.Float(description="density"),
    'kdisFW': fields.Float(description="kdisFW"),
    'kdisFWsed': fields.Float(description="kdisFWsed"),
    'kdisSW': fields.Float(description="kdisSW"),
    'kdisSWsed': fields.Float(description="kdisSWsed"),
    'kdisS1': fields.Float(description="kdisS1"),
    'kdisS2': fields.Float(description="kdisS2"),
    'kdisS3': fields.Float(description="kdisS3"),
    'kdisS4': fields.Float(description="kdisS4"),
    'ksedFW': fields.Float(description="ksedFW"),
    'ksedSW': fields.Float(description="ksedSW"),
    'khetA': fields.Float(description="khetA"),
    'khetFW': fields.Float(description="khetFW"),
    'khetSW': fields.Float(description="khetSW"),
    'elutionS1': fields.Float(description="elutionS1"),
    'elutionS2': fields.Float(description="elutionS2"),
    'elutionS3': fields.Float(description="elutionS3"),
    'elutionS4': fields.Float(description="elutionS4"),
    'enrichFactor': fields.Float(description="enrichFactor")
})

MetalParams = enmNamespace.model('MetalParams', {
    'name': fields.String(description="name"),
    'chem_formula': fields.String(description="chem_formula"),
    'type': fields.String(description="type"),
    'MW': fields.Float(description="MW"),
    'Kaw_n': fields.Float(description="Kaw_n"),
    'enrichFactor': fields.Float(description="enrichFactor"),
    'Fr_air_p': fields.Float(description="Fr_air_p"),
    'Fr_air_c': fields.Float(description="Fr_air_c"),
    'Fr_air_i': fields.Float(description="Fr_air_i"),
    'Fr_fw_p': fields.Float(description="Fr_fw_p"),
    'Fr_fw_c': fields.Float(description="Fr_fw_c"),
    'Fr_fw_i': fields.Float(description="Fr_fw_i"),
    'Fr_fwSed_p': fields.Float(description="Fr_fwSed_p"),
    'Fr_fwSed_c': fields.Float(description="Fr_fwSed_c"),
    'Fr_fwSed_i': fields.Float(description="Fr_fwSed_i"),
    'Fr_sw_p': fields.Float(description="Fr_sw_p"),
    'Fr_sw_c': fields.Float(description="Fr_sw_c"),
    'Fr_sw_i': fields.Float(description="Fr_sw_i"),
    'Fr_swSed_p': fields.Float(description="Fr_swSed_p"),
    'Fr_swSed_c': fields.Float(description="Fr_swSed_c"),
    'Fr_swSed_i': fields.Float(description="Fr_swSed_i"),
    'Fr_soil1_p': fields.Float(description="Fr_soil1_p"),
    'Fr_soil1_c': fields.Float(description="Fr_soil1_c"),
    'Fr_soil1_i': fields.Float(description="Fr_soil1_i"),
    'Fr_soil2_p': fields.Float(description="Fr_soil2_p"),
    'Fr_soil2_c': fields.Float(description="Fr_soil2_c"),
    'Fr_soil2_i': fields.Float(description="Fr_soil2_i"),
    'Fr_soil3_p': fields.Float(description="Fr_soil3_p"),
    'Fr_soil3_c': fields.Float(description="Fr_soil3_c"),
    'Fr_soil3_i': fields.Float(description="Fr_soil3_i"),
    'Fr_soil4_p': fields.Float(description="Fr_soil4_p"),
    'Fr_soil4_c': fields.Float(description="Fr_soil4_c"),
    'Fr_soil4_i': fields.Float(description="Fr_soil4_i")
})

ENM = enmNamespace.model('ENM', {
    '_id': fields.String(description="Document ID"),
    'userId': fields.String(description="User's ID"),
    'params': fields.Raw(description="Parameters")
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


@enmNamespace.route('/', methods=['POST', 'PUT', 'GET', 'DELETE'])
class MainClass(Resource):

    enm_dao = ENMDao(mongoClient=mongoClient)

    @enmNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'}, security='Bearer')
    @enmNamespace.param('id', 'id')
    @enmNamespace.param('maximum', 'maximum')
    @token_required
    def get(self,):
        args = parser.parse_args()
        id = args.get('id')
        maximum = args.get('maximum')

        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)
        if id is None:
            enm_q, total = self.self.enm_dao.find(
                {'userId': userid, 'maximum': maximum})
            enms = []
            for r in enm_q:
                enms.append(json_util.dumps(r))
            resp = Response(json.dumps(enms))
            resp.headers["Access-Control-Expose-Headers"] = '*'
            resp.headers["total"] = total
            return resp
        else:
            enm_q = self.enm_dao.find_one({'userId': userid, '_id': id})
            resp = Response(json_util.dumps(enm_q))
            resp.headers["Access-Control-Expose-Headers"] = '*'
            return resp


@enmNamespace.route('/<string:material>')
class PostPut(Resource):

    enm_dao = ENMDao(mongoClient=mongoClient)

    @enmNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'},security='Bearer')
    @enmNamespace.expect(ENM)
    @enmNamespace.response(ENM, description="The new Material")
    @token_required
    def post(self, material):
        enm: dict = request.json
        if material == 'nonIon' and sorted(enm['params'].keys()) == sorted(NonIonizableParams.keys()):
            cont = True
            enmType = 'NonionizableOrganic'
        elif material == 'ion' and sorted(enm['params'].keys()) == sorted(IonizableParams.keys()):
            cont = True
            enmType = 'IonizableOrganic'
        elif material == 'nanomaterial' and sorted(enm['params'].keys()) == sorted(NanomaterialParams.keys()):
            cont = True
            enmType = 'Nanomaterial'
        elif material == 'metal' and sorted(enm['params'].keys()) == sorted(MetalParams.keys()):
            cont = True
            enmType = 'Metal'
        else:
            cont = False


        if cont:
            token = request.headers['Authorization']
            token = token.split(' ')[1]
            userid = oidc.user_getfield('sub', token)

            enm['userId'] = userid
            enmId = randomString(14)
            enm['_id'] = enmId
            enm['type'] = enmType
            enm = self.enm_dao.insert_one(enm)

            resp = Response(json.dumps(enm))
        else:
            resp = Response()
            resp.status_code = 400
            resp.status = "Malformed Input"

        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp

    @enmNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'},security='Bearer')
    @enmNamespace.expect(ENM)
    @enmNamespace.response(ENM, description="The new Material")
    @token_required
    def put(self, material):
        enm: dict = request.json
        print('K')
        if material == 'nonIon' and sorted(enm['params'].keys()) == sorted(NonIonizableParams.keys()):
            cont = True
        elif material == 'ion' and sorted(enm['params'].keys()) == sorted(IonizableParams.keys()):
            cont = True
        elif material == 'nanomaterial' and sorted(enm['params'].keys()) == sorted(NanomaterialParams.keys()):
            cont = True
        elif material == 'metal' and sorted(enm['params'].keys()) == sorted(MetalParams.keys()):
            cont = True
        else:
            cont = False


        if cont:
            token = request.headers['Authorization']
            token = token.split(" ")[1]
            userid = oidc.user_getfield('sub', token)

            query = {"userId": userid, '_id': enm['_id']}
            reg = self.enm_dao.update_one(query, enm)

            resp = Response(json.dumps(reg))
        else:
            resp = Response()
            resp.status_code = 400
            resp.status = "Malformed Input"

        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp

@enmNamespace.route('/<string:enm_id>')
class DeleteEmission(Resource):

    enm_dao = ENMDao(mongoClient=mongoClient)

    @enmNamespace.doc(responses={200: 'OK', 400: 'Bad request', 500: 'Server Error'},
                                                     security='Bearer')
    @token_required
    def delete(self, enm_id):
        token = request.headers['Authorization']
        token = token.split(" ")[1]
        userid = oidc.user_getfield('sub', token)

        enm_id = self.enm_dao.delete_one(userid, enm_id)

        resp = Response(json.dumps({"deleted": 1}))
        resp.headers["Access-Control-Expose-Headers"] = '*'
        return resp


def randomString(stringLength=10):
    """Generate a random string of letters, digits """
    password_characters = string.ascii_letters + string.digits + string.ascii_letters
    return ''.join(random.choice(password_characters) for i in range(stringLength))
