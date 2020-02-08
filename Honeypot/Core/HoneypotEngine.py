"""
    run the app and all services
"""

from Honeypot.Core.ServiceController import ServiceController
from Honeypot.Settings.HoneypotSettings import Settings
from time import sleep, time


class HoneypotUI:

    success_marker = "\t[+] "
    info_marker = "\t[*] "
    fail_marker = "\t[-] "
    success = "\tSUCCESS"
    fail = "\tFAIL"

    def __init__(self):
        self.print_start_info()

    def get_status(self, ok):
        if ok:
            return self.success
        else:
            return self.fail

    def print_start_info(self):
        print("========================= Honeypot v" + Settings.__version__ + " =========================")

    def get_marker(self, status):
        if status:
            return self.success_marker
        else:
            return self.fail_marker

    def print_loading_settings(self, ok=True):
        print(self.get_marker(ok) + "Loading settings:\t" + self.get_status(ok))

    def print_starting_services_info(self, ok=True):
        print(self.success_marker + "Loading services:\t" + self.get_status(ok))

    def print_processes_info(self, pids):
        print(self.success_marker + "Processes started:")
        for pid in pids:
            print("\t" + self.info_marker + pid[0] + "\tPID: " + str(pid[1]))

    def print_info(self, info):
        print(info)

    def print_terminate_info(self, ok=True):
        print(self.success_marker + "Terminating processes:" + self.get_status(ok))

    def print_end_info(self):
        print("============================= Exiting ==============================")


class HoneypotEngine:

    service_controller = None
    ui = None
    work_time = 0

    def __init__(self):
        self.service_controller = ServiceController()
        self.ui = HoneypotUI()
        self.work_time = Settings.work_time

    def run(self):
        self.init()
        try:
            self.ui.print_info(self.ui.info_marker + self.get_working_time())
            self.ui.print_info(self.ui.info_marker + "Press Ctrl-C to exit")
            self.run_loop()
        except KeyboardInterrupt:
            self.ui.print_info(self.ui.info_marker + "Honeypot stopped.")
            pass
        except Exception as e:
            print(str(e))
        finally:
            self.clean()

    def run_loop(self):
        if self.work_time == 0:
            self.inf_loop()
        else:
            self.time_loop()

    def inf_loop(self):
        while 1:
            sleep(1)

    def time_loop(self):
        start_time = time()
        current_time = 0
        while (current_time - start_time) < self.work_time:
            sleep(1)
            current_time = time()

    def init(self):
        self.ui.print_loading_settings()
        status = self.service_controller.start_services()
        self.ui.print_starting_services_info(status)
        self.ui.print_processes_info(self.service_controller.get_names_and_pids())

    def get_working_time(self):
        if self.work_time != 0:
            return "Honeypot will be running for: " + str(self.work_time) + " seconds and will shut down."
        else:
            return "Honeypot will be running continuously."

    def clean(self):
        status = self.service_controller.stop_services()
        self.ui.print_terminate_info(status)
        self.ui.print_end_info()
