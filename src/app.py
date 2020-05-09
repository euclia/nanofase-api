import httplib2
from werkzeug.utils import cached_property
from flask import Flask, url_for
from flask_restx import Api
h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)
from flask_cors import CORS
from src.namespaces.emissions_namespace import emissionNamespace as emissionApi
from src.globals.globals import oidc, mongoClient
import os
import json
from werkzeug.middleware.proxy_fix import ProxyFix


# with open('/nanofase-api/conf/client_s.json') as json_file:
#     data = json.load(json_file)

with open('./config/client_s.json') as json_file:
    data = json.load(json_file)

# client_secret = '24c9410f-935f-499d-aca4-1e52ae496cbf'
client_secret = data['web']['client_secret']
debug = data['web']['debug']


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

CORS(app)

# app.config.update({
#     'SECRET_KEY': client_secret,
#     'TESTING': True,
#     'DEBUG': True,
#     'OIDC_CLIENT_SECRETS': "/nanofase-api/conf/client_s.json",
#     'OIDC_ID_TOKEN_COOKIE_SECURE': False,
#     'OIDC_REQUIRE_VERIFIED_EMAIL': False,
#     'OIDC_USER_INFO_ENABLED': True,
#     'OIDC_OPENID_REALM': 'jaqpot',
#     'OIDC_SCOPES': ['openid', 'email', 'profile'],
#     'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
# })

app.config.update({
    'SECRET_KEY': client_secret,
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': "./config/client_s.json",
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'jaqpot',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

authorizations = {
    'Bearer': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

if os.environ.get('HTTPS'):
    @property
    def specs_url(self):
        return url_for(self.endpoint('specs'), _external=True, _scheme='https')


nfapi = Api(app=app, version='1.0'
            , title="NanoFase"
            , description='NanoFase API', authorizations=authorizations)

# ddapi.specs_url = specs_url()

nfapi.add_namespace(emissionApi)
# ddapi.add_namespace(imageApi)
# ddapi.add_namespace(taskApi)

oidc.init_app(app)

if __name__ == "__main__":
    if debug == "true":
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=False)
