from vehicle_manager import VehicleManager
from event_processor import EventProcessor
from communication_terminal import CommunicationTerminal
import time




if __name__ == '__main__':
    vm = VehicleManager()
    vm.initialize()
    ep = EventProcessor(vm)
    ep.start()
    CommunicationTerminal.setEventProcessor(ep)
    CommunicationTerminal.startServer()

    while True:
        time.sleep(5)