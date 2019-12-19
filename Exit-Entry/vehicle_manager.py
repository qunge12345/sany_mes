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
from replyer import Replyer
from trans_order_manager import TransportOrderManager
import traceback

class VehicleManager(object):
    '''
    manager of vehicles
    '''
    tom = TransportOrderManager(serverIP = "127.0.0.1", serverPort = 55200)

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

        rt = threading.Thread(target = VehicleManager.realtimeReportHandler, name = 'vehicle_realtime_report' , args = (self,))
        rt.setDaemon(True)
        rt.start()

    def getIdleAndEmptyVehicles(self):
        return [v for v in self._vehicles.values() if v.getStatus() == VehicleState.IDLE and \
        ((v.getAvailableNum() == 0 and v.getType() in [VehicleType.HX_LOADER, VehicleType.XD_LOADER]) or \
        (v.getType() == VehicleType.HX_TRANS and v.getLoaderAvailableNum() == 0 ))]

    def getIdleAndFullVehicles(self):
        return [v for v in self._vehicles.values() if v.getStatus() == VehicleState.IDLE and \
        ((v.getAvailableNum() == 0 and v.getType() in [VehicleType.HX_UNLOADER, VehicleType.XD_UNLOADER]) or \
        (v.getType() == VehicleType.HX_TRANS and v.getUnloaderAvailableNum() == 0))]

    def listenHandler(self):
        '''
        listen from redis
        '''
        # establish redis
        r = redis.StrictRedis(host = '192.168.2.100', port = 6379, db = 0)
        p = r.pubsub()
        p.psubscribe("SW:VehicleStatus:*")

        #listening
        for item in p.listen():
            bmsg = item.get('data',b'')
            if isinstance(bmsg, bytes):
                msg = json.loads(bmsg.decode())
                vehicleName = msg.get('vehicle_id')

                if self._vehicles.get(vehicleName) is None:
                    # a new vehicle is added
                    self._vehicles[vehicleName] = globals()[vehicleName.split('-')[0]](vehicleName)

                self._vehicles[vehicleName].setTimestamp(datetime.datetime.now())
                self._vehicles[vehicleName].updateByInfo(msg)
            

    def maintenanceHandler(self):
        '''
        set timeout for any vehicle which has been online ever before
        '''
        while True:
            # sleep for 2 second
            time.sleep(2.0)
            now = datetime.datetime.now()
            # update vehicles' info
            vehicles = []
            try:
                vehicles = VehicleManager.tom.getVehiclesInfo()
            except Exception as e:
                self._log.error('get vehicles information error: ' + e)
                self._log.error(traceback.format_exc())
                return
            # loop through the vehicles
            for v in self._vehicles.values():
                try:
                    if (now - v.getLatastStamp()).seconds > 10:
                        self._log.warn('vehicle %s lost information' % v.getName())
                        v.setOnline(False)
                    orderNames = [ve.get('transportOrder') for ve in vehicles if ve.get('name') == v.getName()]
                    tempStr = ''
                    self._log.info(v.getName() + ' has orders:')
                    self._log.info(orderNames)
                    if len(orderNames) > 0 and None != orderNames[0]:
                        orderName = orderNames[0]
                        self._log.info(v.getName() + ' gets order name:' + orderName)
                        tempStrs = orderName.split('-')
                        if len(tempStrs) > 0:
                            tempStr = tempStrs[0]
                            self._log.info(v.getName() + ' gets order first string:' + tempStr)

                    v.updateReportState(tempStr)
                    Replyer.sendMessage(v.getStateReportJson())
                except Exception as e:
                    self._log.error(traceback.format_exc())
                    self._log.error(e)


    def realtimeReportHandler(self):
        '''
        realtime report thread
        '''
        while True:
            # sleep for 5 second
            time.sleep(1.0)

            # update vehicles' realtime data
            vehicles = []
            for v in self._vehicles.values():
                vehicles.append(v.getRealtimeReport())

            # send
            report = {}
            report['msgT'] = 2
            report['data'] = vehicles
            Replyer.sendMessage(json.dumps(report))



    def getAvailableVehicleByEvent(self, deviceEvent):
        '''
        return a vehicle or None

        TODO use config file to bind vehicles and machines !!!!!!!!!!!!!!!!!
        '''
        vlist = []

        deviceType = deviceEvent.getType()
        for v in self._vehicles.values():
            if v.getStatus() == VehicleState.IDLE and  \
            v.getType().value == deviceType.value:
                vlist.append(v)
            
            elif v.getStatus() == VehicleState.IDLE and  \
            deviceType in (DeviceType.HX_LOAD, DeviceType.HX_UNLOAD) and  \
            v.getType() == VehicleType.HX_TRANS:
                vlist.append(v)
        
        if len(vlist) > 0:
            vlist.sort(key = lambda v : v.getAvailableNum(), reverse = True)
            return vlist[0]

        return None

    def show(self):
        for v in self._vehicles.values():
            print(v)


if __name__ == '__main__':
    vm = VehicleManager()
    vm.initialize()
    import time
    while True:
        time.sleep(1)
