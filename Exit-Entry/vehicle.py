import sys
sys.path.append('..')

import json
import utils
from enum import Enum, unique

import abc
import threading
import datetime

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
        self._status = VehicleStatus.UNVAILABLE
        self._type = vehicleType # type is used for classified in vehicles
        self._name = vehicleName # name is used for update from json string
        self._availableList = []
        self._latastStamp = datetime.datetime.now()

    @abc.abstractmethod
    def updateByInfo(self, info):
        pass

        # update the timestamp
        self._latastStamp = datetime.datetime.now()

    @utils.mb_lock_and_catch
    def setStatus(self, status):
        self._status = status

    @utils.mb_lock_and_catch
    def getStatus(self):
        return self._status

    def getName(self):
        return self._name

    def getType(self):
        return self._type

    @utils.mb_lock_and_catch
    def getLatastStamp(self):
        return self._latastStamp

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

    @utils.mb_lock_and_catch
    def updateByInfo(self, info):
        self._availableList = info.get('DI')[0:6]
        if info.get('dispatch_state') == 2: # ERROR == 2
            self._status = VehicleStatus.ERROR


class XdUnloaderVehicle(Vehicle):
    
    def __init__(self, vehicleName):
        super(XdUnloaderVehicle, self).__init__(VehicleType.XD_UNLOADER, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        return len(self._availableList) - sum(self._availableList)

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return [i for i,x in enumerate(self._availableList) if x == 0]

    @utils.mb_lock_and_catch
    def updateByInfo(self, info):
        self._availableList = list(map(int, info.get('DI')))
        if info.get('dispatch_state') == 2: # ERROR == 2
            self._status = VehicleStatus.ERROR

        # print(self._availableList)


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

    @utils.mb_lock_and_catch
    def updateByInfo(self, info):
        self._availableList = info.get('DI')[0:6]
        if info.get('dispatch_state') == 2: # ERROR == 2
            self._status = VehicleStatus.ERROR


class HxUnloaderVehicle(Vehicle):
    
    def __init__(self, vehicleName):
        super(HxUnloaderVehicle, self).__init__(VehicleType.HX_UNLOADER, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        return len(self._availableList) - sum(self._availableList)

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return [i for i,x in enumerate(self._availableList) if x == 0]

    @utils.mb_lock_and_catch
    def updateByInfo(self, info):
        self._availableList = info.get('DI')[0:6]
        if info.get('dispatch_state') == 2: # ERROR == 2
            self._status = VehicleStatus.ERROR

    
if __name__ == '__main__':
    
    hxv = HxLoaderVehicle('hexin1')
    hxv.updateByInfo({"DI":[1,0,1,1,0,0,1,1,1,1],"status":"ERROR"})
    print(hxv.getAvailableIndexList())
    print(hxv.getAvailableNum())
    print(hxv.getStatus())
    print(hxv.getName())
