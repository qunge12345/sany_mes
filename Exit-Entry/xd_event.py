
from enum import Enum, unique
import json
import utils
import sys

sys.path.append("..")

@unique
class DeviceType(Enum):
    XD_LOAD = 0
    XD_UNLOAD = 1
    HX_LOAD = 2
    HX_UNLOAD = 3
    UNKNOW = 4

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
        self._machineName = self._data.get('machine_code')# + '-01'
        self._machineIP = self._data.get('machine_ip')
        self._timestamp = self._data.get('time')
        self._version = self._data.get('version')

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

    def __str__(self):
        return self._machineName + ":" + self._deviceType.name + ":" + self._info
        
        


if __name__ == '__main__':
    pass