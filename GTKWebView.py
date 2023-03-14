import signal, queue

from datetime import datetime

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2


GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)


class Printer:
    print_settings: Gtk.PrintSettings

    def __init__(self):
        self.print_settings = Gtk.PrintSettings()
        self.print_settings.set(Gtk.PRINT_SETTINGS_OUTPUT_FILE_FORMAT, 'pdf')
        self.print_settings.set(Gtk.PRINT_SETTINGS_PRINTER, 'Print to File')

    def finished_print(self, operation):
        print('finished_print')
        return True
    def failed_print(self, operation, error):
        print('failed_print', error)
        Gtk.main_quit()
        return True
    def load_failed(self, webview, error):
        print('load_failed', error)
        return True
    def load_changed(self, webview, event):
        print('load_changed', event)
        if WebKit2.LoadEvent.FINISHED == event:
            webview.run_javascript('print();')
        return True
    def process_print(self, webview, operation):
        print('process_print')
        self.print_settings.set(Gtk.PRINT_SETTINGS_OUTPUT_URI, 'file:///tmp/pdf/'+str(datetime.now())+'.pdf')
        operation.set_print_settings(self.print_settings)
        operation.connect('finished', self.finished_print)
        operation.connect('failed', self.failed_print)
        operation.print_()
        return True

class Window(Gtk.Window):
    def load_uri_queue(self, webview: WebKit2.WebView, q: queue.Queue):
        try:
            url = q.get(False)
        except queue.Empty:
            return GLib.SOURCE_CONTINUE
        print('load_uri', url)
        q.task_done()
        webview.load_uri(url)
        return GLib.SOURCE_CONTINUE

    def main(self, app_queue):
        self.connect('destroy', Gtk.main_quit)

        printer = Printer()

        webview = WebKit2.WebView()
        webview.connect('print', printer.process_print)
        webview.connect('load-changed', printer.load_changed)
        webview.connect('load-failed', printer.load_failed)

        self.add(webview)
        self.show_all()

        GLib.idle_add(self.load_uri_queue, webview, app_queue)

        Gtk.main()
