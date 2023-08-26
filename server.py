from bottle import ServerAdapter


class SipperWSGIRefServer(ServerAdapter):
    """ Custom WSGIRefServer implementation to accommodate shutdown, ssl etc. """
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*arguments, **kw): pass

            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def shutdown(self):
        self.server.server_close()
        self.server.shutdown()
