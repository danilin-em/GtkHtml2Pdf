import threading, sys
from logging import Logger, StreamHandler as LoggerStreamHandler
from queue import Queue

import ApiServer
import GTKWebView

app_logger = Logger('app')
app_logger.addHandler(LoggerStreamHandler(sys.stdout))

request_queue = Queue()
response_queue = Queue()

def web_view(req_queue: Queue, resp_queue: Queue, log: Logger):
    log.debug('web_view')
    window = GTKWebView.Window()
    window.main(req_queue, resp_queue, log)

def http_server(req_queue: Queue, resp_queue: Queue, log: Logger):
    log.debug('http_server')
    api_server = ApiServer.Server(req_queue, resp_queue, log)
    api_server.serve_forever()

threading.Thread(target=web_view, args=(request_queue, response_queue, app_logger, )).start()
threading.Thread(target=http_server, args=(request_queue, response_queue, app_logger, )).start()
