
class Settings:
    """ Honeypot Core Settings"""

    __version__ = '1.0.0'

    # default project dir
    default_project_dir = "Honeypot"

    # default services' directory
    default_service_dir = "Services"

    # list of all services suitable for emulation
    services = ["HTTPService", "SSHService", "SMTPService"]

    # default work time of Honeypot
    # set the value in seconds
    # 0 - represents infinity
    work_time = 0

    """ Logging Settings """

    # default log directory
    default_log_dir = default_project_dir + "//Logs"

