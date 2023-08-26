from abc import abstractmethod


class Authentication:
    def __init__(self, enabled=False, mechanism=None):
        self.enabled = enabled
        self.mechanism = mechanism
        self.failed_status_code = 401
        self.failed_message = 'Access Denied.'

    @abstractmethod
    def decorate_with_auth_required(self, res):
        pass

    @abstractmethod
    def authenticate(self, header):
        pass


class BasicAuthentication(Authentication):

    def __init__(self, realm='', enabled=False, username=None, password=None):
        Authentication.__init__(self, enabled=enabled, mechanism='Basic')
        self.username = username
        self.password = password
        self.realm = realm
        self.__header_regex = r'Basic (?P<credentials>.*)'
        self.__username_password_regex = r'(?P<username>.*):(?P<password>.*)'

    def decorate_with_auth_required(self, res):
        res.set_header('WWW-Authenticate', 'Basic realm="%s"' % self.realm)
        res.set_header('Content-Type', 'text/html')
        res.status = self.failed_status_code
        res.body = self.failed_message

    def authenticate(self, header):
        import re
        basic_header_match = re.match(self.__header_regex, header)
        if basic_header_match is None:
            return False
        credentials = basic_header_match.group('credentials')
        from base64 import b64decode
        decoded = b64decode(credentials).decode('utf-8')
        username_password_match = re.match(self.__username_password_regex, decoded)
        if username_password_match is None:
            return False
        username = username_password_match.group('username')
        password = username_password_match.group('password')
        return self.username == username and self.password == password
