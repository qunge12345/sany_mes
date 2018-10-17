import sys
sys.path.append('..')

from vehicle import *
from xd_event import *
from vehicle_manager import *
from slot_adapter import *

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
            return

        # get the value of evt type
        evtTypeValue = evt.getType().value

        # override the out-of-date event
        for i,e in enumerate(self._queues[evtTypeValue]):
            if e.getMachineName() == evt.getMachineName():
                self._queues[evtTypeValue][i] = evt
                return

        self._queues[evtTypeValue].append(evt)

    @utils.mb_lock_and_catch
    def scan(self):
        '''
        scan the queues and create pairs of vehicle--event
        '''
        # reload work
        for vehicle in self._vehicles.getIdleAndFullVehicles():
            TaskManager.createReloadTask(vehicle)

        # normal work
        for queue in self._queues:
            # no event
            if len(queue) == 0:
                continue

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
            time.sleep(1.0)
            self.scan()


    def start(self):
        st = threading.Thread(target = EventProcessor.scaningHandler, name = 'event scaning' , args = (self,))
        st.setDaemon(True)
        st.start()
            

        



if __name__ == '__main__':
    vm = VehicleManager()
    vm.initialize()
    ep = EventProcessor(vm)
    ep.start()