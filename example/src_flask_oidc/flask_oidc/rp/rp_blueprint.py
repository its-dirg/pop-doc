# pylint: disable=no-name-in-module,import-error
from flask import Blueprint
from flask import abort
from flask import request
from flask import session
from flask.ext.login import UserMixin
from flask.ext.login import login_user
from flask.ext.login import login_required
from flask.ext.login import logout_user
from flask.helpers import url_for, flash
from jinja2 import TemplateNotFound
from oic.utils.http_util import Redirect
from flask_oidc.rp import USER_STORE
from flask_oidc.rp.oidc import OIDCError

__author__ = 'mathiashedstrom'


class User(UserMixin):
    def __init__(self, user_id):
        self.id = None
        self.user_info = None
        try:
            user = USER_STORE[user_id]
            self.id = user_id
            self.user_info = user["user_info"]
        except KeyError:
            pass


def _login_user(user_info):
    user_id = user_info["sub"]
    if user_id not in USER_STORE:
        USER_STORE[user_id] = {
            'user_info': user_info
        }
    user = User(user_id)
    login_user(user)


class OIDCRPBlueprint(Blueprint):
    LOGIN_SUCCESS_ENDPOINT = "login_succ_endpoint"
    LOGIN_ERROR_ENDPOINT = "login_err_endpoint"
    LOGOUT_SUCCESS_ENDPOINT = "logout_succ_endpoint"

    def __init__(self, clients, acr_values, login_manager, custom_endpoints=None):
        super(OIDCRPBlueprint, self).__init__('oidc_rp', __name__,
                                              template_folder='templates')
        self.clients = clients
        self.acr_values = acr_values
        self.custom_endpoints = custom_endpoints

        login_manager.user_loader(self._load_user)

        self.add_url_rule("/rp", "connect_op", self._connect_op)
        self.add_url_rule("/authz_cb", "authenticate", self._authenticate)
        self.add_url_rule("/logout", "logout", login_required(self._logout))

    def _connect_op(self):
        try:
            query = request.args
            if "uid" in query:
                client = self.clients.dynamic_client(query["uid"])
                session["op"] = client.provider_info["issuer"]
            else:
                client = self.clients[query["op"]]
                session["op"] = query["op"]

            try:
                resp = client.create_authn_request(session, self.acr_values)
            except Exception:
                raise
            else:
                return resp
        except TemplateNotFound:
            abort(404)

    def _authenticate(self):
        query = request.args
        client = self.clients[session["op"]]
        try:
            result = client.callback(query, session)
            if isinstance(result, Redirect):
                return result
            _login_user(result)
        except OIDCError as err:
            flash(str(err))
            return Redirect(
                message=url_for(
                    self.custom_endpoints.get(OIDCRPBlueprint.LOGIN_ERROR_ENDPOINT, "/")))
        except Exception:
            raise
        return Redirect(
            message=url_for(
                self.custom_endpoints.get(OIDCRPBlueprint.LOGIN_SUCCESS_ENDPOINT, "/")))

    def _logout(self):
        logout_user()
        return Redirect(
            message=url_for(
                self.custom_endpoints.get(OIDCRPBlueprint.LOGOUT_SUCCESS_ENDPOINT, "/")))

    def _load_user(self, user_id):
        return User(user_id)
