import treq
import requests
import json
import logging
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

        headers = {'X-Application': self.app_key, 'Content-Type': 'application/x-www-form-urlencoded'}
        resp = requests.post('https://identitysso.betfair.com/api/certlogin',
                data='username='+username+'&password='+password,
                cert=('certs/betfair.crt', 'certs/betfair.key'), headers=headers)
        
        if resp.json()['loginStatus'] == 'SUCCESS':
          print 'Logged in.'
          self.session_token=resp.json()['sessionToken']
          print self.session_token
        else:
          print resp.json()['loginStatus']


    def __identity_request(self, method):

        if method=="keepAlive":
            message = "Still alive."
        elif method=="logout":
            message = "Logged out successfully."
        else:
            message = "Unknown success."
            
        self.logger.debug("network.__identity_request")
        print self.session_token
        resp = requests.post(
            url="https://identitysso.betfair.com/api/" + method,
            headers={
                "X-Application": self.app_key,
                "X-Authentication": self.session_token,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"}
        )
        utils.check_status_code(resp)
        if resp.json()['status'] != 'SUCCESS':
            print "Request failed."
            print resp.json()['status']
        else:
            print message
            if method=="logout":
                self.session_token==""
 

    def keep_alive(self):
        self.__identity_request("keepAlive")


    def logout(self):
        self.__identity_request("logout")


    def logged_in(self):
        if self.session_token is not None:
            return True
        else:
            return False

