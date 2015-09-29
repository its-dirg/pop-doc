#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,import-error,no-name-in-module
import json
import ssl
import sys
import logging

from oic.utils.authn.authn_context import AuthnBroker
from oic.utils.authn.multi_auth import AuthnIndexedEndpointWrapper
from oic.utils.authn.user import UsernamePasswordMako
from oic.utils import shelve_wrapper
from oic.utils.authn.client import verify_client
from oic.utils.authz import AuthzHandling
from oic.utils.keyio import keyjar_init
from oic.utils.userinfo import UserInfo

from oic.utils.userinfo.aa_info import AaUserInfo
from mako.lookup import TemplateLookup

from jwkest import as_unicode

from example.pop_op import APP
from flask.ext.oidc.op.op_blueprint import OIDCOPBlueprint, make_auth_verify
from pop.PoPProvider import PoPProvider

__author__ = 'rohe0002'

LOGGER = logging.getLogger("")
LOGFILE_NAME = 'oc.log'
HDLR = logging.FileHandler(LOGFILE_NAME)
BASE_FORMATTER = logging.Formatter(
    "%(asctime)s %(name)s:%(levelname)s %(message)s")

CPC = ('%(asctime)s %(name)s:%(levelname)s '
       '[%(client)s,%(path)s,%(cid)s] %(message)s')
CPC_FORMATTER = logging.Formatter(CPC)

HDLR.setFormatter(BASE_FORMATTER)
LOGGER.addHandler(HDLR)
LOGGER.setLevel(logging.DEBUG)

URLMAP = {}
NAME = "pyoic"
OAS = None

PASSWD = {
    "diana": "krall",
    "babs": "howes",
    "upper": "crust"
}


# ----------------------------------------------------------------------------

ROOT = './'

LOOKUP = TemplateLookup(directories=[ROOT + 'templates', ROOT + 'htdocs'],
                        module_directory=ROOT + 'modules',
                        input_encoding='utf-8', output_encoding='utf-8')


# ----------------------------------------------------------------------------

def create_authn_broker(config, lookup, password):
    ac = AuthnBroker()
    end_points = config.AUTHENTICATION["UserPassword"]["END_POINTS"]
    full_end_point_paths = ["%s%s" % (config.issuer, ep) for ep in end_points]
    username_password_authn = UsernamePasswordMako(
        None, "login.mako", lookup, password, "%sauthorization" % config.issuer,
        None, full_end_point_paths)

    for authkey, value in config.AUTHENTICATION.items():
        authn = None

        if "UserPassword" == authkey:
            PASSWORD_END_POINT_INDEX = 0
            end_point = config.AUTHENTICATION[authkey]["END_POINTS"][
                PASSWORD_END_POINT_INDEX]
            authn = AuthnIndexedEndpointWrapper(username_password_authn,
                                                PASSWORD_END_POINT_INDEX)
            APP.add_url_rule("/{}".format(end_point), end_point, make_auth_verify(authn.verify),
                             methods=['GET', 'POST'])

        if "JavascriptLogin" == authkey:
            pass
        if "SAML" == authkey:
            pass
        if "SamlPass" == authkey:
            pass
        if "JavascriptPass" == authkey:
            pass

        if authn is not None:
            ac.add(config.AUTHENTICATION[authkey]["ACR"], authn,
                   config.AUTHENTICATION[authkey]["WEIGHT"],
                   "")
    return ac


if __name__ == '__main__':
    import argparse
    import importlib
    from oic.utils.sdb import SessionDB

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-v', dest='verbose', action='store_true')
    PARSER.add_argument('-d', dest='debug', action='store_true')
    PARSER.add_argument('-p', dest='port', default=80, type=int)
    PARSER.add_argument('-k', dest='insecure', action='store_true')
    PARSER.add_argument(
        '-c', dest='capabilities',
        help="A file containing a JSON representation of the capabilities")
    PARSER.add_argument('-b', dest='baseurl', help="base url of the OP")
    PARSER.add_argument(dest="config")
    ARGS = PARSER.parse_args()

    # Client data base
    CDB = shelve_wrapper.open("client_db")

    sys.path.insert(0, ".")
    CONFIG = importlib.import_module(ARGS.config)
    if ARGS.baseurl:
        CONFIG.baseurl = ARGS.baseurl

    CONFIG.issuer = CONFIG.issuer.format(base=CONFIG.baseurl, port=ARGS.port)
    CONFIG.SERVICE_URL = CONFIG.SERVICE_URL.format(issuer=CONFIG.issuer)

    # dealing with authorization
    AUTHZ = AuthzHandling()

    KWARGS = {
        "template_lookup": LOOKUP,
        "template": {"form_post": "form_response.mako"},
    }

    # Should I care about verifying the certificates used by other entities
    if ARGS.insecure:
        KWARGS["verify_ssl"] = False
    else:
        KWARGS["verify_ssl"] = True

    if ARGS.capabilities:
        KWARGS["capabilities"] = json.loads(open(ARGS.capabilities).read())
    else:
        pass

    AC = create_authn_broker(CONFIG, LOOKUP, PASSWD)

    OAS = PoPProvider(CONFIG.issuer, SessionDB(CONFIG.baseurl), CDB, AC, None,
                      AUTHZ, verify_client, CONFIG.SYM_KEY, **KWARGS)
    OAS.baseurl = CONFIG.issuer

    if CONFIG.USERINFO == "SIMPLE":
        # User info is a simple dictionary in this case statically defined in
        # the configuration file
        OAS.userinfo = UserInfo(CONFIG.USERDB)
    elif CONFIG.USERINFO == "SAML":
        OAS.userinfo = UserInfo(CONFIG.SAML)
    elif CONFIG.USERINFO == "AA":
        OAS.userinfo = AaUserInfo(CONFIG.SP_CONFIG, CONFIG.issuer, CONFIG.SAML)
    else:
        raise Exception("Unsupported userinfo source")

    try:
        OAS.cookie_ttl = CONFIG.COOKIETTL
    except AttributeError:
        pass

    try:
        OAS.cookie_name = CONFIG.COOKIENAME
    except AttributeError:
        pass

    if ARGS.debug:
        OAS.debug = True

    try:
        JWKS = keyjar_init(OAS, CONFIG.keys, kid_template="op%d")
    except Exception as err:
        LOGGER.error("Key setup failed: %s" % err)
        OAS.key_setup("static", sig={"format": "jwk", "alg": "rsa"})
    else:
        NEW_NAME = "static/jwks.json"
        f = open(NEW_NAME, "w")

        for key in JWKS["keys"]:
            for k in key.keys():
                key[k] = as_unicode(key[k])

        f.write(json.dumps(JWKS))
        f.close()
        OAS.jwks_uri.append("%s%s" % (OAS.baseurl, NEW_NAME))

    for b in OAS.keyjar[""]:
        LOGGER.info("OC3 server keys: %s" % b)

    OP_BLUEPRINT = OIDCOPBlueprint(OAS)
    APP.register_blueprint(OP_BLUEPRINT)

    HTTPS = ""
    CONTEXT = None
    if CONFIG.SERVICE_URL.startswith("https"):
        HTTPS = "using HTTPS"
        CONTEXT = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        CONTEXT.load_cert_chain(CONFIG.SERVER_CERT, CONFIG.SERVER_KEY)

    print("OC server starting listening on port:%s %s" % (ARGS.port, HTTPS))
    APP.run(ssl_context=CONTEXT, host='0.0.0.0', port=ARGS.port, debug=True)
