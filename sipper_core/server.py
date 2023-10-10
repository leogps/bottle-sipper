from bottle import ServerAdapter


class SipperCherootServer(ServerAdapter):
    """ Custom WSGIRefServer implementation to accommodate shutdown, ssl etc. """
    server = None

    def __init__(self, host='127.0.0.1', port=8080,
                 ssl_enabled=False,
                 ssl_cert=None,
                 ssl_key=None,
                 silent=False):
        super().__init__(host, port)
        self.ssl_enabled = ssl_enabled
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.silent = silent

    def run(self, handler):
        from cheroot import wsgi
        from cheroot.ssl import builtin

        self.options['bind_addr'] = (self.host, self.port)
        self.options['wsgi_app'] = handler

        self.server = wsgi.Server(**self.options)

        if self.ssl_enabled:
            # Configure SSL context with certificates
            self.server.ssl_adapter = builtin.BuiltinSSLAdapter(
                self.ssl_cert, self.ssl_key)
        self.server.start()

    def shutdown(self):
        self.server.stop()
        self.server = None
