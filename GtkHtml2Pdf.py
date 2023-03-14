import threading, queue

import ApiServer
import GTKWebView

base_queue = queue.Queue()

def web_view(app_queue):
    print('web_view')
    window = GTKWebView.Window()
    window.main(app_queue)

def http_server(app_queue):
    print('http_server')
    api_server = ApiServer.Server(app_queue)
    api_server.serve_forever()

threading.Thread(target=web_view, args=(base_queue,)).start()
threading.Thread(target=http_server, args=(base_queue,)).start()
