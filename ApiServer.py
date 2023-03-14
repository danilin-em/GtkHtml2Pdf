import queue

from http.server import BaseHTTPRequestHandler, HTTPServer as BaseHTTPServer
from urllib.parse import urlparse
from urllib.parse import parse_qs

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)
        input_url = parse_qs(parsed_path.query)['url'][0]
        self.server.app_queue.put(input_url)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("OK: "+input_url, "utf-8"))

class HTTPServer(BaseHTTPServer):
    app_queue: object

    def __init__(self, app_queue: queue.Queue, server_address: tuple[str, int], RequestHandlerClass=RequestHandler):
        self.app_queue = app_queue
        BaseHTTPServer.__init__(self, server_address, RequestHandlerClass)

class Server:
    port: int
    host: str
    http_server: HTTPServer
    def __init__(self, app_queue):
        self.host = "0.0.0.0"
        self.port = 8000
        self.http_server = HTTPServer(app_queue, (self.host, self.port), RequestHandler)
    def serve_forever(self):
        print("Server started http://%s:%s" % (self.host, self.port))
        try:
            self.http_server.serve_forever()
        except KeyboardInterrupt:
            pass
        self.http_server.server_close()
        print("Server stopped.")
