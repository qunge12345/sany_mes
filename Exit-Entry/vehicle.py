import sys
sys.path.append('..')

import json
import utils
from enum import Enum, unique

import abc
import threading
import datetime
import redis
import math

@unique
class VehicleType(Enum):
    XD_LOADER = 0
    XD_UNLOADER = 1
    HX_LOADER = 2
    HX_UNLOADER = 3
    HX_TRANS = 4
    XD_ARM = 5
    HX_ARM = 6
    UNKNOW = 7

@unique
class VehicleState(Enum):
    IDLE = 1
    PROCEEDING = 2
    ERROR = 3   # only get ERROR state from json string !
    UANVAILABLE = 4

class VehicleDispatchStatus(Enum):
    UNKNOWN	= 0
    UNAVAILABLE = 1
    ERROR = 2
    IDLE = 3
    EXECUTING = 4
    CHARGING = 5

class ReportState(Enum):
    U = 0 # upload
    D = 1 # download
    C = 2 # charging
    F = 3 # reload, fetch
    R = 4 # park, rest
    S = 5 # drop, send
    E = 6 # error
    O = 7 # offline

class Vehicle(metaclass = abc.ABCMeta):

    '''
    abstract vehicle 
    '''
    r = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 0)
    
    def __init__(self, vehicleType, vehicleName):
        self._log = utils.logger().getLogger(vehicleName)
        self._lock = threading.Lock()
        self._status = VehicleState.IDLE
        self._type = vehicleType # type is used for classified in vehicles
        self._name = vehicleName # name is used for update from json string
        self._availableList = []
        self._latastStamp = datetime.datetime.now()

        self._state = ReportState.O
        self._runTime = 0
        self._upNo = 0
        self._downNo = 0
        self._odo = 0
        self._vel = 0
        self._batLevel = 0
        self._batVol = 0
        self._batTemp = 0
        self._dispatchState = VehicleDispatchStatus.IDLE.value
        self._isOnline = True
        self._pos = ''
        self._angle = 0
        self._stop = True
        # slots is _availableList

        self._historyTime = 0
        self._historyOdo = 0
        self._historyUpNo = 0
        self._historyDownNo = 0
        self._historyQuan = 0

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
    def setOnline(self, isOnline):
        self._isOnLine = isOnline

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

    @utils.mb_lock_and_catch
    def getStateReportJson(self):
        report = {}
        report['msgT'] = 1
        report['name'] = self._name
        report['state'] = self._state.name
        report['up'] = self._upNo
        report['hisUp'] = self._historyUpNo
        report['down'] = self._downNo
        report['hisDown'] = self._historyDownNo
        report['time'] = self._runTime
        report['hisTime'] = self._historyTime
        report['batLevel'] = self._batLevel
        report['batVol'] = self._batVol
        report['batTemp'] = self._batTemp
        report['type'] = self._type.value
        report['slots'] = self._availableList
        return json.dumps(report)

    @utils.mb_lock_and_catch
    def getRealtimeReport(self):
        report = {}
        report['name'] = self._name
        report['pos'] = self._pos
        report['ang'] = self._angle
        report['stop'] = self._stop
        return report

    @utils.mb_lock_and_catch
    def addUpNo(self, number):
        keyDate = self._name + ':upNoDate'
        keyHistoryUpNo = self._name + ':historyUpNo'
        keyUpNo = self._name + ':upNo'
        # total
        historyUp = Vehicle.r.get(keyHistoryUpNo)
        if None == historyUp:
            historyUp = 0
        self._historyUpNo = int(historyUp) + number
        Vehicle.r.set(keyHistoryUpNo, self._historyUpNo)
        # compare date
        lastDate = Vehicle.r.get(keyDate)
        if lastDate == None or lastDate.decode('utf-8') != str(datetime.date.today()):
            # date is change
            Vehicle.r.set(keyDate, datetime.date.today())
            Vehicle.r.set(keyUpNo, 0)
        upNo = Vehicle.r.get(keyUpNo)
        if None == upNo:
            upNo = 0
        self._upNo = int(upNo) + number
        Vehicle.r.set(keyUpNo, self._upNo)

    @utils.mb_lock_and_catch
    def addDownNo(self, number):
        keyDate = self._name + ':downNoDate'
        keyHistoryDownNo = self._name + ':historyDownNo'
        keyDownNo = self._name + ':downNo'
        # total
        historyDown = Vehicle.r.get(keyHistoryDownNo)
        if None == historyDown:
            historyDown = 0
        self._historyDownNo = int(historyDown) + number
        Vehicle.r.set(keyHistoryDownNo, self._historyDownNo)
        # compare date
        lastDate = Vehicle.r.get(keyDate)
        if lastDate == None or lastDate.decode('utf-8') != str(datetime.date.today()):
            # date is change
            Vehicle.r.set(keyDate, datetime.date.today())
            Vehicle.r.set(keyDownNo, 0)
        downNo = Vehicle.r.get(keyDownNo)
        if None == downNo:
            downNo = 0
        self._downNo = int(downNo) + number
        Vehicle.r.set(keyDownNo, self._downNo)

    # This is invoked internal, so not use lock
    def updateCommonInfo(self, info):
        self._isOnline = True
        self._runTime = int(info.get('time') / 1000) # ms to s
        self._historyTime = int(info.get('total_time') / 1000) # ms to s
        self._odo = int(info.get('today_odo'))
        self._historyOdo = int(info.get('odo'))
        self._batLevel = info.get('battery_level')
        self._batTemp = info.get('battery_temp')
        self._batVol = info.get('voltage')
        self._dispatchState = info.get('dispatch_state')
        self._pos = info.get('current_station')
        self._angle = int(info.get('angle') * 180 / math.pi)
        self._stop = False if info.get('vx') > 0.2 else True

    @utils.mb_lock_and_catch
    def updateReportState(self, possibleState):
        state = self._state
        if self._dispatchState == VehicleDispatchStatus.ERROR.value:
            state = ReportState.E
        elif self._dispatchState == VehicleDispatchStatus.CHARGING.value:
            state = ReportState.C
        elif self._dispatchState == VehicleDispatchStatus.UNAVAILABLE.value or self._isOnline == False:
            state = ReportState.O
        elif possibleState == 'Upload':
            state = ReportState.U
        elif possibleState == 'Download':
            state = ReportState.D
        elif possibleState == 'Reload':
            state = ReportState.F
        elif possibleState == 'Drop':
            state = ReportState.S
        else:
            state = ReportState.R

        if self._state != state:
            self._state = state
            return True

        return False

    
class XdUploader(Vehicle):

    def __init__(self, vehicleName):
        super(XdUploader, self).__init__(VehicleType.XD_LOADER, vehicleName)

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

        self.updateCommonInfo(info)

class XdDownloader(Vehicle):
    
    def __init__(self, vehicleName):
        super(XdDownloader, self).__init__(VehicleType.XD_UNLOADER, vehicleName)

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

        self.updateCommonInfo(info)

class HxLoader(Vehicle):
    
    def __init__(self, vehicleName):
        super(HxLoader, self).__init__(VehicleType.HX_TRANS, vehicleName)
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

        self.updateCommonInfo(info)

    def __str__(self):
        return self._name + " : " + self._type.name  + " : " + self._status.name + \
        " : " + self._latastStamp.strftime('%Y-%m-%d-%H-%M-%S') + " : " + str(self._loaderAvailableList) + " : " + str(self._UnloaderAvailableList)


class HxUploader(Vehicle):
    
    def __init__(self, vehicleName):
        super(HxUploader, self).__init__(VehicleType.HX_LOADER, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        # TODO, this is for test
        return sum(self._availableList)

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return [i for i,x in enumerate(self._availableList) if x > 0]

    @utils.mb_lock_and_catch
    def updateByInfo(self, info):
        self.updateCommonInfo(info)

class HxDownloader(Vehicle):
    
    def __init__(self, vehicleName):
        super(HxDownloader, self).__init__(VehicleType.HX_UNLOADER, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        return len(self._availableList) - sum(self._availableList)

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return [i for i,x in enumerate(self._availableList) if x == 0]

    @utils.mb_lock_and_catch
    def updateByInfo(self, info):
        self.updateCommonInfo(info)

class XdArm(Vehicle):
    
    def __init__(self, vehicleName):
        super(XdArm, self).__init__(VehicleType.XD_ARM, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        return 0

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return []

    @utils.mb_lock_and_catch
    def updateByInfo(self, info):
        self.updateCommonInfo(info)

class HxArm(Vehicle):
    
    def __init__(self, vehicleName):
        super(HxArm, self).__init__(VehicleType.HX_ARM, vehicleName)

    @utils.mb_lock_and_catch
    def getAvailableNum(self):
        return 0

    @utils.mb_lock_and_catch
    def getAvailableIndexList(self):
        return []

    @utils.mb_lock_and_catch
    def updateByInfo(self, info):
        self.updateCommonInfo(info)

    
if __name__ == '__main__':
    r = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 0)
    r.set('a', datetime.date.today())
    print (r.get('a').decode('utf-8'))
    print (str(datetime.date.today()))
