from vehicle import *
from xd_event import *

class VehicleManager(object):
    '''
    manager of vehicles
    '''

    def __init__(self):
        pass

    def initialize(self):
        '''
        start to run listener and maintenance
        '''
        pass

    def listenHandler(self):
        pass

    def maintenanceHandler(self):
        '''
        set timeout for any vehicle which has been online ever before
        '''
        pass

    def getAvailableVehicleByEvent(self, DeviceType):
        '''
        return a vehicle or none
        '''
        pass


if __name__ == '__main__':