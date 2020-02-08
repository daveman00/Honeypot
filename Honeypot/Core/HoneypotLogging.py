"""
    class responsible for handling all the logging and storing it in proper log files
"""

import logging
import os
import datetime
from Honeypot.Settings.HoneypotSettings import Settings


class HoneypotLogging:
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def __init__(self, name):
        self.setup_logger(name)

    def setup_logger(self, name, log_level=logging.DEBUG):
        log_file = os.getcwd() + "//" + Settings.default_log_dir + "//" + name + "//" + name \
                        + "_" + str(datetime.date.today()) + ".log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        handler = logging.FileHandler(log_file)
        handler.setFormatter(self.formatter)

        logger = self.get_logger(name)
        logger.setLevel(log_level)
        logger.addHandler(handler)

        return logger

    def get_logger(self, name):
        return logging.getLogger(name)


