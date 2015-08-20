# pylint: disable=missing-docstring,too-few-public-methods
from oic.utils.http_util import Response

__author__ = 'mathiashedstrom'


class FlaskResponse(Response):
    def __init__(self, call_args=None, **kwargs):
        super(FlaskResponse, self).__init__(**kwargs)
        self.call_args = call_args

    def __call__(self, environ, start_response):
        return super(FlaskResponse, self).__call__(environ, start_response, **self.call_args)
