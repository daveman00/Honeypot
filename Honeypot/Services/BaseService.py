""" Base service class template """


from Honeypot.Core.HoneypotLogging import HoneypotLogging


class Service:
    service_id = 0
    logger_name = None
    port = None

    def __init__(self):
        self.service_id = Service.service_id
        Service.service_id += 1

    def setup_logging(self, logger_name):
        self.logger_name = logger_name
        return HoneypotLogging(logger_name)

    def initialize(self):
        pass

    def run(self):
        pass

    def shutdown(self):
        pass

