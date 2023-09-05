from bottle import ServerAdapter
import ssl


class SipperWSGIRefServer(ServerAdapter):
    """ Custom WSGIRefServer implementation to accommodate shutdown, ssl etc. """
    server = None

    def __init__(self, host='127.0.0.1', port=8080,
                 ssl_enabled=False,
                 ssl_cert=None,
                 ssl_key=None,
                 silent=False,
                 **options):
        super().__init__(host, port, **options)
        self.ssl_enabled = ssl_enabled
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.silent = silent

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                if self.silent:
                    def log_request(*arguments, **kw): pass
                else:
                    pass

            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)

        if self.ssl_enabled:
            # Configure SSL context with certificates
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=self.ssl_cert, keyfile=self.ssl_key)

            # Wrap the server with SSL/TLS context
            self.server.socket = ssl_context.wrap_socket(
                self.server.socket,
                server_side=True
            )
        self.server.serve_forever()

    def shutdown(self):
        self.server.server_close()
        self.server.shutdown()
