import sys
sys.path.append('..')

from vehicle import *
from xd_event import *
from vehicle_manager import *
from slot_adapter import *
from task_manager import TaskManager

import utils
import json
import time
import datetime
import threading
from collections import deque

class EventProcessor(object):

    MAX_LEN = 200

    def __init__(self, vehicles, loggerName = 'event queue'):
        self._log = utils.logger().getLogger(loggerName)
        self._lock = threading.Lock()
        self._vehicles = vehicles
        self._queues = ( \
        deque(maxlen = EventProcessor.MAX_LEN), \
        deque(maxlen = EventProcessor.MAX_LEN), \
        deque(maxlen = EventProcessor.MAX_LEN), \
        deque(maxlen = EventProcessor.MAX_LEN))

    @utils.mb_lock_and_catch
    def pushMessage(self, eventStr):
        # create event by json string
        evt = XDEvent(eventStr)
        if evt.getType() == DeviceType.UNKNOW:
            self._log.info('unknown status: ' + evt.getMachineName() + ' info: ' + evt.getMachineInfo())
            return

        # get the value of evt type
        evtTypeValue = evt.getType().value

        # override the out-of-date event
        isMerge = False
        currentQueue = self._queues[evtTypeValue]
        
        # only Xiong Di needs to merge info
        if evt.getType() in (DeviceType.XD_LOAD, DeviceType.XD_UNLOAD):
            for i,e in enumerate(currentQueue):
                if e.getMachineName() == evt.getMachineName():
                    evt.mergeInfoFrom(currentQueue[i])
                    self._log.info('event merge and override: ' + evt.getMachineName() + ' ' + evt.getType().name +  ': ' + e.getMachineInfo() + ' --> ' + evt.getMachineInfo())
                    currentQueue[i] = evt
                    isMerge = True
                    break
        
        if False == isMerge:
            currentQueue.append(evt)

    @utils.mb_lock_and_catch
    def show(self):
        for que in self._queues:
            for e in que:
                print(e)

    @utils.mb_lock_and_catch
    def scan(self):
        '''
        scan the queues and create pairs of vehicle--event
        '''
        # reload work, reload when get device signal
        # for vehicle in self._vehicles.getIdleAndEmptyVehicles():
        #     TaskManager.createReloadTask(vehicle)

        for vehicle in self._vehicles.getIdleAndFullVehicles():
            TaskManager.createDropTask(vehicle)

        # normal work
        for queue in self._queues:
            # no event
            if len(queue) == 0:
                continue

            # check event nearby vehicle TODO

            # 
            evt = queue[0]
            vehicle = self._vehicles.getAvailableVehicleByEvent(evt)

            # no available vehicle
            if None == vehicle:
                continue
            
            queue.popleft()
            TaskManager.createNormalTask(evt, vehicle)

    def scaningHandler(self):
        '''
        loop the scan task
        '''
        while True:
            time.sleep(0.5)
            self.scan()


    def start(self):
        st = threading.Thread(target = EventProcessor.scaningHandler, name = 'event scaning' , args = (self,))
        st.setDaemon(True)
        st.start()

if __name__ == '__main__':
    # vm = VehicleManager()
    # vm.initialize()
    # ep = EventProcessor(vm)
    # ep.start()
    d = deque(maxlen = EventProcessor.MAX_LEN)
    d.append('aa')
    d.append('bb')
    d.append('cc')
    print(d)
    t = d[2]
    d.remove(t)
    d.appendleft(t)
    print(d)

