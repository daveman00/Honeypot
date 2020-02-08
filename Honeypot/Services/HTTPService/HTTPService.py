""" HTTP service emulation """

from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from os import path
import logging
from Honeypot.Services.BaseService import Service
from Honeypot.Settings.HTTPSettings import HTTPServerSettings

LOGGER = None


class HTTPHandler(BaseHTTPRequestHandler):

    BaseHTTPRequestHandler.server_version = HTTPServerSettings.server_version
    BaseHTTPRequestHandler.sys_version = HTTPServerSettings.system_version
    BaseHTTPRequestHandler.protocol_version = HTTPServerSettings.protocol_version

    def set_headers(self, length, code=200, msg='OK'):
        self.flush_headers()
        self.send_response(code, msg)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", length)
        self.end_headers()

    def get_main_page_name(self):
        for page in HTTPServerSettings.main_pages:
            page_path = str(HTTPServerSettings.pages_dir + "/" + page)
            if path.isfile(page_path):
                return page_path

    def do_GET(self):
        page_name = self.get_main_page_name()
        with open(page_name) as page:
            contents = page.read().encode("utf-8")
        self.set_headers(len(contents))
        self.wfile.write(contents)
        self.print_request_data()

    def do_POST(self):
        self.do_GET()

    def send_error(self, code, message=None, explain=None):
        self.set_headers(500, "ERROR")
        self.wfile.write("Not supported.".encode("utf-8"))

    def log_error(self, format, *args):
        self.log_message(format, *args)
        return

    def log_message(self, format, *args):
        logging.getLogger(LOGGER).error(str(args))
        return

    def print_request_data(self):
        logging.getLogger(LOGGER).info("--- REQUEST DATA START ---")
        logging.getLogger(LOGGER).warning("client_address: %s" % str(self.client_address))
        logging.getLogger(LOGGER).info("request: %s" % str(self.requestline))
        logging.getLogger(LOGGER).info("command: %s" % str(self.command))
        logging.getLogger(LOGGER).info("path: %s" % str(self.path))
        logging.getLogger(LOGGER).info("request_version: %s" % str(self.request_version))
        logging.getLogger(LOGGER).info("headers: \n%s" % str(self.headers))
        logging.getLogger(LOGGER).info("raw_request: %s" % str(self.raw_requestline))
        logging.getLogger(LOGGER).info("--- REQUEST DATA END ---")


class HHTTPServer(HTTPServer, ThreadingMixIn):
    pass


class HTTPService(Service):

    handler_class = HTTPHandler
    server_class = HHTTPServer
    server_class.server_name = HTTPServerSettings.server_version + " (" + HTTPServerSettings.system_version + ")"
    server_class.timeout = HTTPServerSettings.timeout

    server_address = (HTTPServerSettings.bind_address, HTTPServerSettings.server_port)

    def serve(self):
        with self.server_class(self.server_address, self.handler_class) as httpd:
                httpd.serve_forever()

    def initialize(self):
        self.port = HTTPServerSettings.server_port
        self.setup_logging(type(self).__name__)
        global LOGGER
        LOGGER = self.logger_name

    def run(self):
        self.initialize()
        self.serve()

    def shutdown(self):
        pass

