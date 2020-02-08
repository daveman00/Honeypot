""" SSH server emulation using Paramiko """


from Honeypot.Services.BaseService import Service
from Honeypot.Settings.SSHSettings import SSHServerSettings
import paramiko
import socket
import threading
import logging
from time import time

HOST_KEY = paramiko.RSAKey(filename=SSHServerSettings.private_rsa)
LOGGER = None


class SSHServer(paramiko.ServerInterface):

    def __init__(self):
        super().__init__()
        self.event = threading.Event()

    # low level interaction - no login available
    def check_auth_password(self, username, password):
        logging.getLogger(LOGGER).info("Username: " + username)
        logging.getLogger(LOGGER).info("Password: " + password)
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        else:
            return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def print_collected_data(self, username, password):
        print("Username: " + username)
        print("Password: " + password)


class SSHService(Service):
    server = None
    sock = None
    timeout = None
    protocol_version = "SSH-2.0-"

    def initialize(self):
        self.setup_logging(type(self).__name__)
        global LOGGER
        LOGGER = self.logger_name
        self.timeout = SSHServerSettings.timeout
        self.server = SSHServer()
        self.sock = socket.socket()
        self.port = SSHServerSettings.server_port
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((SSHServerSettings.bind_address, self.port))

    def run(self):
        self.initialize()
        while True:
            self.server_listen()

    def server_listen(self):

        try:
            self.sock.listen()
            client, addr = self.sock.accept()
            session = self.get_session(client)
            logging.getLogger(LOGGER).warning("Incoming connection from: %s" % repr(addr))

            try:
                session.start_server(server=self.server)
                begin = time()
                while True:
                    session.accept(20)
                    if not session.is_active():
                        session.close()
                        break
                    else:
                        end = time()
                        if (end - begin) >= self.timeout:
                            session.close()
                            raise Exception("Connection timed out")

            except Exception as e:
                logging.getLogger(LOGGER).error(str(e))
                session.close()

        except Exception as e:
            logging.getLogger(LOGGER).error("Socket exception: " + str(e))

    def get_socket(self):
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((SSHServerSettings.bind_address, SSHServerSettings.server_port))
        return sock

    def get_session(self, client):
        session = paramiko.Transport(client)
        session.set_hexdump(True)
        session.set_log_channel(self.logger_name)
        session.add_server_key(HOST_KEY)
        session.local_version = self.protocol_version + SSHServerSettings.server_version
        return session

    def print_collected_data(self, addr):
        logging.getLogger(LOGGER).warning("Incoming connection from: %s" % repr(addr))


