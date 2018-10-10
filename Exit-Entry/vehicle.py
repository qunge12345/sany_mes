import sys
sys.path.append('..')

import json
import utils
from enum import Enum, unique

import abc
import threading


@unique
class VehicleType(Enum):
    XD_LOADER = 0
    XD_UNLOADER = 1
    HX_LOADER = 2
    HX_UNLOADER = 3
    UNKNOW = 4

@unique
class VehicleStatus(Enum):
    IDLE = 1
    PROCEEDING = 2
    ERROR = 3   # only get ERROR state from json string !
    UNVAILABLE = 4

class Vehicle(metaclass = abc.ABCMeta):

    '''
    abstract vehicle 
    '''
    
    def __init__(self, vehicleType, vehicleName):
        self._log = utils.logger().getLogger(vehicleName)
        self._lock = threading.Lock()
        self._status = VehicleStatus.IDLE
        self._vehicleType = vehicleType # type is used for classified in vehicles
        self._vehicleName = vehicleName # name is used for update from json string
        self._availableList = []

    @utils.mb_lock_and_catch
    def updateByJsonString(self, jsonStr):
        tempData = json.loads(jsonStr)
        self._availableList = tempData.get('available_list')
        if tempData.get('status') == 'ERROR':
            self.setStatus(VehicleStatus.ERROR)

    def setStatus(self, status):
        self._status = status

    def getStatus(self):
        return self._status

    def getName(self):
        return self._vehicleName

    def getType(self):
        return self._vehicleType

    @abc.abstractmethod
    def getAvailableNum(self):
        pass

    @abc.abstractmethod
    def getAvailableIndexList(self):
        pass


    
class XdLoaderVehicle(Vehicle):

    def __init__(self, vehicleName):
        super(XdLoaderVehicle, self).__init__(VehicleType.XD_LOADER, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        # TODO, this is for test
        return sum(self._availableList)

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return [i for i,x in enumerate(self._availableList) if x > 0]


class XdUnloaderVehicle(Vehicle):
    
    def __init__(self, vehicleName):
        super(XdUnloaderVehicle, self).__init__(VehicleType.XD_UNLOADER, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        return len(self._availableList) - sum(self._availableList)

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return [i for i,x in enumerate(self._availableList) if x == 0]


class HxLoaderVehicle(Vehicle):
    
    def __init__(self, vehicleName):
        super(HxLoaderVehicle, self).__init__(VehicleType.HX_LOADER, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        # TODO, this is for test
        return sum(self._availableList)

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return [i for i,x in enumerate(self._availableList) if x > 0]


class HxUnloaderVehicle(Vehicle):
    
    def __init__(self, vehicleName):
        super(HxUnloaderVehicle, self).__init__(VehicleType.HX_UNLOADER, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        return len(self._availableList) - sum(self._availableList)

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return [i for i,x in enumerate(self._availableList) if x == 0]
    
if __name__ == '__main__':
    
    hxv = HxLoaderVehicle('hexin1')
    hxv.updateByJsonString('{"available_list":[1,0,1,1,0,0,1],"status":"ERROR"}')
    print(hxv.getAvailableIndexList())
    print(hxv.getAvailableNum())
    print(hxv.getStatus())
    print(hxv.getName())
