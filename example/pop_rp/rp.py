# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,import-error,no-name-in-module
import logging
import argparse
import importlib
import ssl
import six
from six.moves.urllib.parse import urlparse
from mako.lookup import TemplateLookup
from beaker.middleware import SessionMiddleware
from flask.helpers import get_flashed_messages
from flask.sessions import SessionInterface
from flask.ext.login import current_user
from flask.ext.login import login_required
from flask_oidc.rp.oidc import OIDCClients
from flask_oidc.rp.rp_blueprint import OIDCRPBlueprint
from flask_oidc.util.response import FlaskResponse

from example.pop_rp import LOGIN_MANAGER
from example.pop_rp import APP

__author__ = 'mathiashedstrom'

logging.basicConfig(level=logging.DEBUG)

LOOKUP = TemplateLookup(directories=['templates', 'htdocs'],
                        module_directory='modules',
                        input_encoding='utf-8',
                        output_encoding='utf-8')


def opchoice(clients):
    argv = {
        "op_list": list(clients.keys())
    }
    return FlaskResponse(call_args=argv, mako_template="opchoice.mako",
                         template_lookup=LOOKUP,
                         headers=[])


def opresult():
    argv = {
        "userinfo": current_user.user_info,
    }
    return FlaskResponse(call_args=argv, mako_template="opresult.mako",
                         template_lookup=LOOKUP, headers=[])


def operror(error=None):
    argv = {
        "error": error
    }
    return FlaskResponse(call_args=argv, mako_template="operror.mako",
                         template_lookup=LOOKUP, headers=[])


@APP.route('/')
def home():
    return opchoice(CLIENTS)


@APP.route('/login_successful')
@login_required
def login_successful():
    return opresult()


@APP.route('/login_error')
def login_fail():
    return operror(get_flashed_messages())


@APP.route('/logout_successful')
def logout_successful():
    return "Logout successful!"


@APP.errorhandler(401)
def error_unauthorized(error):
    return "unauthorized {}".format(error)


@APP.route('/test_authorized')
@login_required
def test_login_needed():
    return "You are authorized"


class BeakerSessionInterface(SessionInterface):
    def open_session(self, app, request):
        session = request.environ['beaker.session']
        return session

    def save_session(self, app, session, response):
        session.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="config")
    parser.add_argument("-p", default=8666, dest="port", help="port of the RP")
    parser.add_argument("-b", dest="base_url", help="base url of the RP")
    args = parser.parse_args()
    conf = importlib.import_module(args.config)

    session_opts = {
        'session.type': 'memory',
        'session.cookie_expires': True,
        'session.auto': True,
        'session.key': "{}.beaker.session.id".format(
            urlparse(conf.BASE).netloc.replace(":", "."))
    }

    APP.wsgi_app = SessionMiddleware(APP.wsgi_app, session_opts)
    APP.session_interface = BeakerSessionInterface()

    conf.BASE = "{base}:{port}/".format(base=conf.BASE, port=args.port)
    conf.ME["redirect_uris"] = [url.format(base=conf.BASE) for url in
                                conf.ME["redirect_uris"]]
    conf.ME["post_logout_redirect_uris"] = [url.format(base=conf.BASE) for url
                                            in conf.ME[
                                                "post_logout_redirect_uris"]]

    for client, client_conf in six.iteritems(conf.CLIENTS):
        if "client_registration" in client_conf:
            client_reg = client_conf["client_registration"]
            client_reg["redirect_uris"] = [url.format(base=conf.BASE) for url in
                                           client_reg["redirect_uris"]]

    global CLIENTS
    CLIENTS = OIDCClients(conf)
    ACR_VALUES = conf.ACR_VALUES

    oidc = OIDCRPBlueprint(CLIENTS, ACR_VALUES, LOGIN_MANAGER,
                           custom_endpoints={
                               OIDCRPBlueprint.LOGIN_SUCCESS_ENDPOINT: "login_successful",
                               OIDCRPBlueprint.LOGIN_ERROR_ENDPOINT: "login_fail",
                               OIDCRPBlueprint.LOGOUT_SUCCESS_ENDPOINT: "logout_successful"})
    APP.register_blueprint(oidc)

    context = None
    if conf.BASE.startswith("https"):
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.load_cert_chain(conf.SERVER_CERT, conf.SERVER_KEY)

    APP.run(ssl_context=context, host='0.0.0.0', port=args.port, debug=True)
