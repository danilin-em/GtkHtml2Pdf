from http.server import BaseHTTPRequestHandler, HTTPServer as BaseHTTPServer
from logging import Logger
from queue import Queue
from urllib.parse import urlparse
from urllib.parse import parse_qs

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)
        input_url = parse_qs(parsed_path.query)['url'][0]
        self.server.request_queue.put(input_url)

        pdf = self.server.response_queue.get()
        self.server.response_queue.task_done()

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("OK: "+pdf, "utf-8"))

class HTTPServer(BaseHTTPServer):
    request_queue: Queue
    response_queue: Queue

    def __init__(self, request_queue: Queue, response_queue: Queue, server_address: tuple[str, int], RequestHandlerClass=RequestHandler):
        self.request_queue = request_queue
        self.response_queue = response_queue
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)

class Server:
    log: Logger
    port: int
    host: str
    http_server: HTTPServer
    def __init__(self, request_queue: Queue, response_queue: Queue, log: Logger):
        self.log = log
        self.host = "0.0.0.0"
        self.port = 8000
        self.http_server = HTTPServer(request_queue, response_queue, (self.host, self.port), RequestHandler)
    def serve_forever(self):
        self.log.debug("Server started http://%s:%s" % (self.host, self.port))
        try:
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            pass
        self.http_server.server_close()
        self.log.debug("Server stopped.")
