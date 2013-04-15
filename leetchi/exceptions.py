class APIError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '%s: %s' % (self.code, self.message)


class DecodeError(APIError):
    def __init__(self, status_code, headers, body):
        super(DecodeError, self).__init__(None, "Could not decode JSON")
        self.body = body
        self.headers = headers
        self.status_code = status_code

    def __repr__(self):
        return "status_code: %s, headers: %s, content: <%s>" % (self.status_code,
                                                                self.headers,
                                                                self.body)
