""" SMTP server emulation using smtpd lib"""


from Honeypot.Services.BaseService import Service
from Honeypot.Settings.SMTPSettings import SMTPServerSettings
import asynchat
import asyncore
import errno
import logging
from smtpd import SMTPServer, SMTPChannel


LOGGER = None
DATA_SIZE_DEFAULT = SMTPServerSettings.data_size
FQDN = SMTPServerSettings.fqdn
SOFTWARE_VERSION = SMTPServerSettings.server_version


class HSMTPChannel(SMTPChannel):

    def __init__(self, server, conn, addr, data_size_limit=DATA_SIZE_DEFAULT,
                 map=None, enable_SMTPUTF8=False, decode_data=False):
        asynchat.async_chat.__init__(self, conn, map=map)
        self.smtp_server = server
        self.conn = conn
        self.addr = addr
        self.data_size_limit = data_size_limit
        self.enable_SMTPUTF8 = enable_SMTPUTF8
        self._decode_data = decode_data
        if enable_SMTPUTF8 and decode_data:
            raise ValueError("decode_data and enable_SMTPUTF8 cannot"
                             " be set to True at the same time")
        if decode_data:
            self._emptystring = ''
            self._linesep = '\r\n'
            self._dotsep = '.'
            self._newline = '\n'
        else:
            self._emptystring = b''
            self._linesep = b'\r\n'
            self._dotsep = ord(b'.')
            self._newline = b'\n'
        self._set_rset_state()
        self.seen_greeting = ''
        self.extended_smtp = False
        self.command_size_limits.clear()
        self.fqdn = FQDN
        try:
            self.peer = conn.getpeername()
        except OSError as err:
            # a race condition  may occur if the other end is closing
            # before we can get the peername
            self.close()

            if err.args[0] != errno.ENOTCONN:
                raise
            return
        self.push('220 %s %s' % (self.fqdn, SOFTWARE_VERSION))

    def push(self, msg):
        logging.getLogger(LOGGER).info(msg)
        asynchat.async_chat.push(self, bytes(
            msg + '\r\n', 'utf-8' if self.require_SMTPUTF8 else 'ascii'))

    def collect_incoming_data(self, data):
        logging.getLogger(LOGGER).info(data)
        limit = None
        if self.smtp_state == self.COMMAND:
            limit = self.max_command_size_limit
        elif self.smtp_state == self.DATA:
            limit = self.data_size_limit
        if limit and self.num_bytes > limit:
            return
        elif limit:
            self.num_bytes += len(data)
        if self._decode_data:
            self.received_lines.append(str(data, 'utf-8'))
        else:
            self.received_lines.append(data)

    def found_terminator(self):
        line = self._emptystring.join(self.received_lines)
        self.received_lines = []
        if self.smtp_state == self.COMMAND:
            sz, self.num_bytes = self.num_bytes, 0
            if not line:
                self.push('500 Error: bad syntax')
                return
            if not self._decode_data:
                try:
                    line = str(line, 'utf-8')
                except:
                    logging.getLogger(LOGGER).info(line)
            i = line.find(' ')
            if i < 0:
                command = line.upper()
                arg = None
            else:
                command = line[:i].upper()
                arg = line[i + 1:].strip()
            max_sz = (self.command_size_limits[command]
                      if self.extended_smtp else self.command_size_limit)
            if sz > max_sz:
                self.push('500 Error: line too long')
                return
            method = getattr(self, 'smtp_' + command, None)
            if not method:
                self.push('500 Error: command "%s" not recognized' % command)
                return
            method(arg)
            return
        else:
            if self.smtp_state != self.DATA:
                self.push('451 Internal confusion')
                self.num_bytes = 0
                return
            if self.data_size_limit and self.num_bytes > self.data_size_limit:
                self.push('552 Error: Too much mail data')
                self.num_bytes = 0
                return
            # Remove extraneous carriage returns and de-transparency according
            # to RFC 5321, Section 4.5.2.
            data = []
            for text in line.split(self._linesep):
                if text and text[0] == self._dotsep:
                    data.append(text[1:])
                else:
                    data.append(text)
            self.received_data = self._newline.join(data)
            args = (self.peer, self.mailfrom, self.rcpttos, self.received_data)
            kwargs = {}
            if not self._decode_data:
                kwargs = {
                    'mail_options': self.mail_options,
                    'rcpt_options': self.rcpt_options,
                }
            status = self.smtp_server.process_message(*args, **kwargs)
            self._set_post_data_state()
            if not status:
                self.push('250 OK')
            else:
                self.push(status)

    def handle_error(self):
        pass


class HSMTPServer(SMTPServer):
    def __init__(self, localaddr, remoteaddr):
        super().__init__(localaddr, remoteaddr)
        self.channel_class = HSMTPChannel

    def handle_accepted(self, conn, addr):
        logging.getLogger(LOGGER).warning('Incoming connection from: %s' % repr(addr))
        channel = self.channel_class(self, conn, addr, self.data_size_limit, self._map,
                                     self.enable_SMTPUTF8, self._decode_data)

    def _print_message_content(self, peer, data):
        inheaders = 1
        lines = data.splitlines()
        for line in lines:
            # headers first
            if inheaders and not line:
                peerheader = 'X-Peer: ' + peer[0]
                if not isinstance(data, str):
                    # decoded_data=false; make header match other binary output
                    peerheader = repr(peerheader.encode('utf-8'))
                inheaders = 0
            if not isinstance(data, str):
                # Avoid spurious 'str on bytes instance' warning.
                line = repr(line)
            logging.getLogger(LOGGER).info(line)

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        logging.getLogger(LOGGER).info('---------- MESSAGE FOLLOWS ----------')
        if kwargs:
            if kwargs.get('mail_options'):
                logging.getLogger(LOGGER).info('mail options: %s' % kwargs['mail_options'])
            if kwargs.get('rcpt_options'):
                logging.getLogger(LOGGER).info('rcpt options: %s\n' % kwargs['rcpt_options'])
        self._print_message_content(peer, data)
        logging.getLogger(LOGGER).info('------------ END MESSAGE ------------')


class SMTPService(Service):

    bind_address = None
    server = None

    def initialize(self):
        self.setup_logging(type(self).__name__)
        global LOGGER
        LOGGER = self.logger_name
        self.bind_address = SMTPServerSettings.bind_address
        self.port = SMTPServerSettings.server_port

    def run(self):
        self.initialize()
        self.server = HSMTPServer((self.bind_address, self.port), None)
        asyncore.loop()

    def shutdown(self):
        pass
