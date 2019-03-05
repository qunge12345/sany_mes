
from enum import Enum, unique
import json
import sys
sys.path.append("..")
sys.path.append('.')

import utils

@unique
class DeviceType(Enum):
    XD_LOAD = 0
    XD_UNLOAD = 1
    HX_LOAD = 2
    HX_UNLOAD = 3
    UNKNOW = 5

@unique
class EventStatus(Enum):
    WAIT = 1
    PROCEEDING = 2

class XDEvent(object):

    def __init__(self, jsonStr):
        '''
        there must be a json string to construct the event
        '''
        self._deviceType = DeviceType.UNKNOW
        self._data = json.loads(jsonStr)
        # which machine
        self._eventSource = self._data.get('event_source')
        self._machineStatus = self._data.get('machine_status')
        # which slot
        self._info = self._data.get('info')
        # machine ip & uid and so on
        self._machineName = self._data.get('machine_code')
        self._machineIP = self._data.get('machine_ip')
        self._timestamp = self._data.get('time')
        self._version = self._data.get('version')
        self._token = self._data.get('token')

        # decide the device type
        if self._eventSource == '0':  # XiongDi
            if self._machineStatus == '4':
                self._deviceType = DeviceType.XD_LOAD
            elif self._machineStatus == '5':
                self._deviceType = DeviceType.XD_UNLOAD
        elif self._eventSource == '1': # HangXin
            if self._machineStatus == '4':
                self._deviceType = DeviceType.HX_LOAD
            elif self._machineStatus == '5':
                self._deviceType = DeviceType.HX_UNLOAD

        self._status = EventStatus.WAIT

    def getMachineName(self):
        return self._machineName

    def getMachineIP(self):
        return self._machineIP

    def getStatus(self):
        return self._status

    def setStatus(self, status):
        self._status = status

    def getMachineInfo(self):
        return self._info

    def getType(self):
        return self._deviceType

    def getEventSource(self):
        return self._eventSource

    def getMachineStatus(self):
        return self._machineStatus

    def getToken(self):
        return self._token

    def mergeInfoFrom(self, evt):
        '''
        merge the given event info to this event
        '''
        # function to merge machine info
        def mergeList(*matrix):
            max_len = max((len(l) for l in matrix))
            new_matrix = list(map(lambda l:l + [0]*(max_len - len(l)), matrix))
            sumList = [0] * len(new_matrix[0])
            for i in range(len(new_matrix)):
                for j in range(len(new_matrix[0])):
                    sumList[j] = sumList[j] + new_matrix[i][j]
            return sumList

        selfInfo = list(map(int, self._info.split(':')))
        evtInfo = list(map(int, evt.getMachineInfo().split(':')))
        newInfo = mergeList(selfInfo, evtInfo)
        # print(':'.join(list(map(str, newInfo))))
        self._info = ':'.join(list(map(str, newInfo)))

    def __str__(self):
        return self._machineName + ":" + self._deviceType.name + ":" + self._info
        
        


if __name__ == '__main__':
    d1 = XDEvent('{         \
    "event_source":"0",\
    "event_status":"0",\
    "info": "1:0",\
    "machine_code": "JC-8000A-89",\
    "machine_ip":"192.168.0.222",\
    "machine_status": "5",\
    "time": "20180404095212",\
    "token":"asdfasdf",\
    "version": "1.0"\
    }')

    d2 = XDEvent('{         \
    "event_source":"0",\
    "event_status":"0",\
    "info": "0:1",\
    "machine_code": "JC-8000A-89",\
    "machine_ip":"192.168.0.222",\
    "machine_status": "5",\
    "time": "20180404095212",\
    "token":"asdfasdf",\
    "version": "1.0"\
    }')

    d1.mergeInfoFrom(d2)
    print(d1.getMachineInfo())