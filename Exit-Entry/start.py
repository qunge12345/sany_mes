from vehicle_manager import VehicleManager
from event_processor import EventProcessor





if __name__ == '__main__':
    vm = VehicleManager()
    vm.initialize()
    ep = EventProcessor(vm)
    ep.start()
