"""
    load all service modules
    manage services as processes
"""

from Honeypot.Settings.HoneypotSettings import Settings
from importlib import import_module
from multiprocessing import Process, set_start_method
import logging


class ServiceController:
    services_names = []
    services = []
    services_processes = []

    def __init__(self):
        set_start_method("spawn")

    def get_modules_names(self):
        # get services' names and their respective modules' names
        modules_names = []
        self.services_names = Settings.services
        for service_name in Settings.services:
            modules_names.append(Settings.default_project_dir + "." + Settings.default_service_dir
                                 + "." + service_name + "." + service_name)
        return modules_names

    def import_modules(self):
        modules = []
        modules_names = self.get_modules_names()
        # import all modules
        for module_name in modules_names:
            modules.append(import_module(module_name))
        return modules

    def load_service_classes(self):
        modules = self.import_modules()
        services_classes = []
        # load services from modules
        for service_name, module in zip(self.services_names, modules):
            services_classes.append(getattr(module, service_name))
        return services_classes

    def initialize_services(self):
        services_classes = self.load_service_classes()
        # init all services
        for service_class in services_classes:
            self.services.append(service_class())

    def spawn_services(self):
        self.initialize_services()
        # spawn services as processes
        for service in self.services:
            self.services_processes.append(Process(target=service.run))

    def start_services(self):
        try:
            self.spawn_services()
            # start processes
            for service in self.services_processes:
                service.start()
        except Exception as e:
            print(str(e))
            return False
        return True

    def stop_services(self):
        # terminate all processes
        try:
            for process in self.services_processes:
                process.terminate()
                process.join()
            self.clean_services()
            logging.shutdown()
            return True
        except Exception as e:
            print(str(e))
            self.clean_services()
            return False

    def clean_services(self):
        for service in self.services:
            service.shutdown()

    def get_names_and_pids(self):
        # returns names of processes and their pids
        pids = []
        for process, name in zip(self.services_processes, self.services_names):
            pids.append((name, process.pid))
        return pids
