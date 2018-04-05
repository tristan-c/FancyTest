import time
from signal import *
import logging

import zmq

from app.models import Configuration
from app.connector import create_connector_by_type
from app.schedulePatched import schedule

port = 7778

class MassiveDaemon():

    def __init__(self,logger=None):
        #where connectors wait to be scheduled
        self.connectorsBuffer = []
        self.runningConnectors = []
        self.logger = logging.getLogger("MassiveDaemon")
        self.logger.setLevel(logging.DEBUG)

        #zmq
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        self.socket.bind("tcp://*:%s" % port)

    def register_new_job(self,configuration):
        self.load_configuration(configuration)
        self.scheduleConnectors()
        self.logger.debug("New job registered, type: %s" % configuration.type)

    def load_configuration(self,configuration):
        self.logger.info("Scheduling on %s job" % configuration.type)
        connector = create_connector_by_type(configuration)
        self.connectorsBuffer.append(connector)

    def load_configurations(self):
        for configuration in Configuration.objects():
            self.load_configuration(configuration)

    def scheduleConnectors(self):
        for connector in self.connectorsBuffer:
            schedule.every(connector.get_refresh_interval()).minutes.do(connector.check)

            # 1500 every 15 mn

            loop = schedule.run_continuously(interval=2)

            # Safe exit threads
            def stopSchedule():
                loop.set()

            for sig in (SIGABRT, SIGTERM):
                signal(sig, stopSchedule)

            self.runningConnectors.append(connector)
            connector.check()

        self.logger.info("%i jobs started" % len(self.connectorsBuffer))
        self.connectorsBuffer = []

    def startDaemon(self):
        self.logger.info("Daemon Start")
        self.load_configurations()
        self.scheduleConnectors()
        self.logger.info("Daemon running")

        try:
            while True:
                try:
                    message = self.socket.recv_json()
                    if message["action"] == "register_new_job":
                        conf = Configuration.objects.get(id=message['id'])
                        self.register_new_job(conf)
                except zmq.ZMQError:
                    # interrupted
                    return

                time.sleep(1)
                self.socket.send_string("World from %s" % port)
        except KeyboardInterrupt:
            self.socket.close()
