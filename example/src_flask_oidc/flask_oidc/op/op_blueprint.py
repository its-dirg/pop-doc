# pylint: disable=no-name-in-module,import-error
import json
import logging
from flask.blueprints import Blueprint
from flask import request
from oic.utils.http_util import BadRequest, Response, extract_from_request, ServiceError, get_post
from oic.utils.webfinger import WebFinger, OIC_ISSUER
import time

__author__ = 'mathiashedstrom'

LOGGER = logging.getLogger(__name__)


def make_auth_verify(callback, next_module_instance=None):
    """
    Closure encapsulating the next module (if any exist) in a multi auth chain.
    :param callback: function to execute for the callback URL at the OP, see UserAuthnMethod.
    verify and its subclasses
    (e.g. SAMLAuthnMethod) for signature
    :param next_module_instance: an object instance of the module next in the chain after
    the module whose verify method
    is the callback -- do not use this parameter!! If you want a multi auth chain see the
    convenience function
    setup_multi_auth (in multi_auth.py)
    :return: function encapsulating the specified callback which properly handles
    a multi auth chain.
    """

    def auth_verify():
        kwargs = extract_from_request(request.environ)
        response, auth_is_complete = callback(**kwargs)
        if auth_is_complete and next_module_instance:
            response = next_module_instance(**kwargs)
        return response

    return auth_verify


def wsgi_wrapper(func, **kwargs):
    kwargs = extract_from_request(request.environ, kwargs)
    args = func(**kwargs)

    try:
        resp, state = args
        return resp
    except TypeError:
        resp = args
        return resp
    except Exception as err:
        LOGGER.error("%s" % err)
        raise


class OIDCOPBlueprint(Blueprint):
    def __init__(self, provider):
        super(OIDCOPBlueprint, self).__init__('oidc_rp', __name__,
                                              template_folder='templates')

        self.provider = provider

        self.add_url_rule("/.well-known/webfinger", "webfinger", self._webfinger)
        self.add_url_rule("/.well-known/openid-configuration", "op_info", self._op_info)
        self.add_url_rule("/registration", "registration", self._registration,
                          methods=['GET', 'POST', ])
        self.add_url_rule("/authorization", "authorization", self._authorization)
        self.add_url_rule("/token", "token", self._token, methods=['GET', 'POST', ])
        self.add_url_rule("/userinfo", "userinfo", self._userinfo, methods=['GET', 'POST', ])
        self.add_url_rule("/keyrollover", "key_rollover", self._key_rollover)
        self.add_url_rule("/clearkeys", "clear_keys", self._clear_keys)

    def _webfinger(self):
        query = request.args
        try:
            assert query["rel"] == OIC_ISSUER
            resource = query["resource"][0]
        except KeyError:
            resp = BadRequest("Missing parameter in request")
        else:
            wf = WebFinger()
            resp = Response(wf.response(subject=resource, base=self.provider.baseurl))
        return resp

    def _op_info(self):
        LOGGER.info("op_info")
        return wsgi_wrapper(self.provider.providerinfo_endpoint, logger=LOGGER)

    def _registration(self):
        environ = request.environ
        if environ["REQUEST_METHOD"] == "POST":
            return wsgi_wrapper(self.provider.registration_endpoint, logger=LOGGER)
        elif environ["REQUEST_METHOD"] == "GET":
            return wsgi_wrapper(self.provider.read_registration, logger=LOGGER)
        else:
            return ServiceError("Method not supported")

    def _authorization(self):
        return wsgi_wrapper(self.provider.authorization_endpoint, logger=LOGGER)

    def _token(self):
        request.environ['oic.url_args'] = request.args
        return wsgi_wrapper(self.provider.token_endpoint,
                            logger=LOGGER)

    def _userinfo(self):
        return self.provider.userinfo_endpoint(self.provider.parse_request(request.environ))

    def _key_rollover(self):
        # expects a post containing the necessary information
        _jwks = json.loads(get_post(request.environ))
        self.provider.do_key_rollover(_jwks, "key_%d_%%d" % int(time.time()))
        return Response("OK")

    def _clear_keys(self):
        self.provider.remove_inactive_keys()
        return Response("OK")
