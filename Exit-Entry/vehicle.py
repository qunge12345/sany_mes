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
    HX_TRANS = 4
    UNKNOW = 5

@unique
class VehicleState(Enum):
    IDLE = 1
    PROCEEDING = 2
    ERROR = 3   # only get ERROR state from json string !
    UNVAILABLE = 4

class VehicleStatus(Enum):
    UNKNOWN	= 0
    UNAVAILABLE = 1
    ERROR = 2
    IDLE = 3
    EXECUTING = 4
    CHARGING = 5


class Vehicle(metaclass = abc.ABCMeta):

    '''
    abstract vehicle 
    '''
    
    def __init__(self, vehicleType, vehicleName):
        self._log = utils.logger().getLogger(vehicleName)
        self._lock = threading.Lock()
        self._status = VehicleState.IDLE
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
    def setState(self, status):
        self._status = status

    @utils.mb_lock_and_catch
    def getStatus(self):
        return self._status

    def getName(self):
        return self._name

    def getType(self):
        return self._type

    def __str__(self):
        return self._name + " : " + self._type.name  + " : " + self._status.name + \
        " : " + self._latastStamp.strftime('%Y-%m-%d-%H-%M-%S') + " : " + str(self._availableList)

    @utils.mb_lock_and_catch
    def getLatastStamp(self):
        return self._latastStamp

    @utils.mb_lock_and_catch
    def setTimestamp(self, timestamp):
        self._latastStamp = timestamp

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
        self._availableList = list(map(int, info.get('DI')))[2:14]
        t1 = self._availableList[2]
        self._availableList[2] = self._availableList[0]
        self._availableList[0] = t1


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
        tl = list(map(int, info.get('DI')))
        self._availableList = [tl[12],tl[10],tl[13],tl[6],tl[11],tl[8]]

class HxVehicle(Vehicle):
    
    def __init__(self, vehicleName):
        super(HxVehicle, self).__init__(VehicleType.HX_TRANS, vehicleName)
        self._loaderAvailableList = []
        self._UnloaderAvailableList = []

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        return 0

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return []

    @utils.mb_lock_and_catch
    def getLoaderAvailableNum(self):
        return sum(self._loaderAvailableList)

    @utils.mb_lock_and_catch
    def getUnloaderAvailableNum(self):
        return len(self._UnloaderAvailableList) - sum(self._UnloaderAvailableList)

    @utils.mb_lock_and_catch
    def getLoaderAvailableIndexList(self):
        return [i for i,x in enumerate(self._loaderAvailableList) if x > 0]

    @utils.mb_lock_and_catch
    def getUnloaderAvailableIndexList(self):
        return [i for i,x in enumerate(self._UnloaderAvailableList) if x == 0]
        
    @utils.mb_lock_and_catch
    def updateByInfo(self, info):
        tl = list(map(int, info.get('DI')))
        # TODO
        self._loaderAvailableList = tl[2:10]
        self._UnloaderAvailableList = tl[10:14]

    def __str__(self):
        return self._name + " : " + self._type.name  + " : " + self._status.name + \
        " : " + self._latastStamp.strftime('%Y-%m-%d-%H-%M-%S') + " : " + str(self._loaderAvailableList) + " : " + str(self._UnloaderAvailableList)


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
        self._availableList = list(map(int, info.get('DI')))[0:6]
        if info.get('dispatch_state') == 2: # ERROR == 2
            self._status = VehicleState.ERROR


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
        self._availableList = list(map(int, info.get('DI')))
        if info.get('dispatch_state') == 2: # ERROR == 2
            self._status = VehicleState.ERROR

    
if __name__ == '__main__':
    
    hxv = HxVehicle('hexin1')
    hxv.updateByInfo({"DI":[True,False,True,True,False,False,True,True,False,True,True,False,False,True,True,False,True,True,False,False,True,True,False,True,True,False,False,True,True,True,True],"status" : "ERROR"})
    print(hxv.getLoaderAvailableIndexList())
    print(hxv.getUnloaderAvailableIndexList())
    print(hxv.getLoaderAvailableNum())
    print(hxv.getUnloaderAvailableNum())
    print(hxv.getStatus())
    print(hxv.getName())
