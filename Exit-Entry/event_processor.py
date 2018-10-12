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

    # deque is thread-safe ?
    # @utils.mb_lock_and_catch
    def pushMessage(self, eventStr):
        # create event by json string
        evt = XDEvent(eventStr)
        self._queues[evt.getType().value].append(evt)

    def scan(self):
        '''
        scan the queues and create pairs of vehicle--event
        '''
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
            TaskManager.createWork(evt, vehicle)

        # reload work
        for vehicle in self._vehicles.getIdleAndFullVehicles():
            TaskManager.createReload(vehicle)

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
    a = deque()
    a.extendleft('1')
    print(a)
    a.extend('2')
    print(a)
    a.extendleft('3')
    print(a)
    a.append('4')
    print(a)
    a.appendleft('5')
    print(a)
    a.pop()
    print(a)
    a.popleft()
    print(a)
    print(len(a))
    print(a[1])
