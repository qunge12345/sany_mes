import sys
sys.path.append('..')

from vehicle import *
from xd_event import *

import utils
import redis
import json
import time
import datetime
import threading

class VehicleManager(object):
    '''
    manager of vehicles
    '''

    def __init__(self, loggerName = 'vehicle manager'):
        self._vehicles = {}
        self._log = utils.logger().getLogger(loggerName)

    def initialize(self):
        '''
        start to run listener and maintenance
        '''
        self._log.info('start vehicle management')

        lt = threading.Thread(target = VehicleManager.listenHandler, name = 'vehicle_redis_listener' , args = (self,))
        lt.setDaemon(True)
        lt.start()
        
        mt = threading.Thread(target = VehicleManager.maintenanceHandler, name = 'vehicle_maintenance' , args = (self,))
        mt.setDaemon(True)
        mt.start()

    def getIdleAndFullVehicles(self):
        return [v for v in self._vehicles.values() if v.getStatus() == VehicleStatus.IDLE and v.getAvailableNum() == 0]

    def listenHandler(self):
        '''
        listen from redis
        '''
        # establish redis
        r = redis.StrictRedis(host = '127.0.0.1', port = 6379, db = 0)
        p = r.pubsub()
        p.psubscribe("SW:VehicleStatus:Carrier_*")

        #listening
        for item in p.listen():
            bmsg = item.get('data',b'')
            if isinstance(bmsg, bytes):
                msg = json.loads(bmsg.decode())
                vehicleName = msg.get('vehicle_id') # e.g. Carrier:XdLoaderVehicle:2

                if self._vehicles.get(vehicleName) is None:
                    # a new vehicle is added
                    self._vehicles[vehicleName] = globals()[vehicleName.split('_')[1]](vehicleName)

                self._vehicles[vehicleName].updateByInfo(msg)
            

    def maintenanceHandler(self):
        '''
        set timeout for any vehicle which has been online ever before
        '''
        while True:
            # sleep for 2 second
            time.sleep(2.0)
            now = datetime.datetime.now()
            # loop through the vehicles
            for v in self._vehicles.values():
                if v.getStatus() != VehicleStatus.UNVAILABLE and (now - v.getLatastStamp()).seconds > 10:
                    self._log.warn('vehicle %s lost information' % v.getName())
                    v.setStatus(VehicleStatus.UNVAILABLE)

    def getAvailableVehicleByEvent(self, deviceEvent):
        '''
        return a vehicle or None
        '''
        deviceType = deviceEvent.getType()
        for v in self._vehicles.values():
            if v.getStatus() == VehicleStatus.IDLE and  \
            v.getType().value == deviceType.value and   \
            v.getAvailableNum() > 0:
                return v

        return None


if __name__ == '__main__':
    vm = VehicleManager()
    vm.initialize()
    import time
    while True:
        time.sleep(1)
