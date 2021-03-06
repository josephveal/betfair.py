# -*- coding: utf-8 -*-


class BetfairError(Exception):
    pass


class BetfairLoginError(BetfairError):

    def __init__(self, response, data):
        self.response = response
        self.message = data.get('loginStatus', 'UNKNOWN')
        super(BetfairLoginError, self).__init__(self.message)


class BetfairAuthError(BetfairError):

    def __init__(self, data): #removed ,response CHANGE
        #self.response = response CHANGE
        self.message = data.get('loginStatus', 'UNKNOWN')
        super(BetfairAuthError, self).__init__(self.message)


class BetfairAPIError(BetfairError):

    def __init__(self, response, data):
        self.response = response
        try:
            error_data = data['error']['data']['APINGException']
            self.message = error_data.get('errorCode', 'UNKNOWN')
            self.details = error_data.get('errorDetails')
        except KeyError:
            self.message = 'UNKNOWN'
            self.details = None
        super(BetfairAPIError, self).__init__(self.message)
