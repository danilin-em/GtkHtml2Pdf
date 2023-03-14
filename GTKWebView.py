import signal, queue

from datetime import datetime
from logging import Logger
from queue import Queue

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2


GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)


class Printer:
    response_queue: Queue
    print_settings: Gtk.PrintSettings
    log: Logger

    def __init__(self, response_queue: Queue, log: Logger):
        self.response_queue = response_queue
        self.log = log
        self.print_settings = Gtk.PrintSettings()
        self.print_settings.set(Gtk.PRINT_SETTINGS_OUTPUT_FILE_FORMAT, 'pdf')
        self.print_settings.set(Gtk.PRINT_SETTINGS_PRINTER, 'Print to File')

    def finished_print(self, operation):
        file = operation.get_print_settings().get(Gtk.PRINT_SETTINGS_OUTPUT_URI)
        self.log.debug('finished_print %s', file)
        self.response_queue.put(file)
        return True
    def failed_print(self, operation, error):
        self.log.debug('failed_print %s', error)
        Gtk.main_quit()
        return True
    def load_failed(self, webview, error):
        self.log.debug('load_failed %s', error)
        return True
    def load_changed(self, webview, event):
        self.log.debug('load_changed %s', event)
        if WebKit2.LoadEvent.FINISHED == event:
            webview.run_javascript('print();')
        return True
    def process_print(self, webview, operation):
        self.log.debug('process_print')
        self.print_settings.set(Gtk.PRINT_SETTINGS_OUTPUT_URI, 'file:///tmp/pdf/'+str(datetime.now().timestamp())+'.pdf')
        operation.set_print_settings(self.print_settings)
        operation.connect('finished', self.finished_print)
        operation.connect('failed', self.failed_print)
        operation.print_()
        return True

class Window(Gtk.Window):
    log: Logger

    def load_uri_queue(self, webview: WebKit2.WebView, request_queue: Queue):
        try:
            url = request_queue.get(False)
        except queue.Empty:
            return GLib.SOURCE_CONTINUE
        self.log.debug('load_uri %s', url)
        request_queue.task_done()
        webview.load_uri(url)
        return GLib.SOURCE_CONTINUE

    def main(self, request_queue: Queue, response_queue: Queue, log: Logger):
        self.log = log
        self.connect('destroy', Gtk.main_quit)

        printer = Printer(response_queue, self.log)

        webview = WebKit2.WebView()
        webview.connect('print', printer.process_print)
        webview.connect('load-changed', printer.load_changed)
        webview.connect('load-failed', printer.load_failed)

        self.add(webview)
        self.show_all()

        GLib.idle_add(self.load_uri_queue, webview, request_queue)

        Gtk.main()
