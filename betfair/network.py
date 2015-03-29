import treq
import requests
import urllib
import json
import logging
from . import exceptions
from . import utils
from constants import Endpoint, Exchange
from twisted.internet.defer import inlineCallbacks, returnValue


class Network(object):
    def __init__(self, app_key="", session_token="", \
            pre_request_action=None, gzip_compress=False):
        self.app_key = app_key
        self.session_token = session_token
        self.pre_request_action = pre_request_action
        self.gzip_compress = gzip_compress
        self.logger = logging.getLogger(name="BetfairNetwork")


    @classmethod
    def __make_json_request(cls, method, params):
        def _dthandler(obj):
            # for datetime objects
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            # for enum objects
            if hasattr(obj, 'name'):
                return obj.name
            if hasattr(obj, 'serialize'):
                return obj.serialize()
            else:
                raise TypeError, "Object of type %s is not JSON serializable" \
                    % type(obj)

        json_resp = {
            "jsonrpc": "2.0",
            "method": method,
            "params": utils.serialize_params(params),
            "id": 1,
        }
        return json.dumps(json_resp, default=_dthandler)


    @classmethod
    def __error_handler(cls, failure):
        from twisted.web import _newclient
        if failure.check(_newclient.RequestGenerationFailed):
            print "printError: RequestGenerationFailed"
            for f in failure.value.reasons:
                print "printError > %r" % f
                print f.getTraceback()


    @inlineCallbacks
    def __request(self, url, data, content_type):
        headers = \
            {"Content-Type": [content_type.encode("ascii", "ignore")], \
            "X-Application": [self.app_key.encode("ascii", "ignore")], \
            "X-Authentication": [self.session_token.encode("ascii", "ignore")]}

        data = data.encode("ascii", "ignore")
        self.logger.debug(url)
        self.logger.debug(headers)
        self.logger.debug(data)

        request = treq.request(method="POST", \
                url=url.encode("ascii", "ignore"), headers=headers, data=data)
        request .addErrback(self.__error_handler)
        resp = yield request
        content = yield treq.content(resp)
        returnValue(content)


    def __request_sync(self, url, data, content_type):
        headers = \
            {"Content-Type": content_type.encode("ascii", "ignore"), \
            "X-Application": self.app_key.encode("ascii", "ignore"), \
            "X-Authentication": self.session_token.encode("ascii", "ignore")}

        data = data.encode("ascii", "ignore")
        self.logger.debug(url)
        self.logger.debug(headers)
        self.logger.debug(data)

        r = requests.post(url, data=data, headers=headers)
        return r


    @inlineCallbacks
    def invoke(self, exchange, endpoint, method, args):
        url = ""
        if exchange == Exchange.AUS:
            url = "https://api-au.betfair.com/exchange"
        else:
            url = "https://api.betfair.com/exchange"

        if endpoint == Endpoint.Betting:
            url = url + "/betting/json-rpc/v1"
        else:
            url = url + "/account/json-rpc/v1"

        request = self.__make_json_request(method, args)
        content = yield self.__request(url, request, "application/json")
        returnValue(utils.result_or_error(content))


    def invoke_sync(self, exchange, endpoint, method, args):
        url = ""
        if exchange == Exchange.AUS:
            url = "https://api-au.betfair.com/exchange"
        else:
            url = "https://api.betfair.com/exchange"

        if endpoint == Endpoint.Betting:
            url = url + "/betting/json-rpc/v1"
        else:
            url = url + "/account/json-rpc/v1"

        request = self.__make_json_request(method, args)
        content = self.__request_sync(url, request, "application/json")
        self.logger.debug(content.text)
        return utils.result_or_error(content)


    def login(self, username, password):
        self.logger.debug("network.login")
        response = requests.post(
            url="https://identitysso-api.betfair.com/api/certlogin",
            cert="certs/betfair.pem",
            data=urllib.urlencode({
                "username": username,
                "password": password
            }),
            headers={
                "X-Application": self.app_key,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        data = response.json()
        if data.get('loginStatus') != 'SUCCESS':
            raise exceptions.BetfairAuthError(data)
        self.session_token = data["sessionToken"]
        self.logger.debug("network login success" + self.session_token)
        return self.session_token

    def logged_in(self):
        if self.session_token is not "":
            return True
        else:
            return False

