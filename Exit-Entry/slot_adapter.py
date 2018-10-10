import sys
sys.path.append('..')

import json
import utils

from vehicle import *
from xd_event import *

class SlotAdapter(object):

    '''
    checkout the available slots pairs between vehicles and devices
    '''
    log = utils.logger().getLogger('slot adapter')

    def __init__(self):
        pass

    @staticmethod
    def checkout(vehicle, deviceEvent):
        '''
        return a list if available pairs, or None
        
        the format of list is : [(vehicle_slot_i, device_slot_i),...]
        '''
        retList = []

        # type mismatch
        if vehicle.getType().value != deviceEvent.getType().value:
            SlotAdapter.log.error("type mismatch : %s --- %s" % (vehicle.getType(), deviceEvent.getType()))
            return None

        if vehicle.getType() == VehicleType.XD_LOADER:
            retList = SlotAdapter.checkXdLoading(vehicle, deviceEvent)
        elif vehicle.getType() == VehicleType.XD_UNLOADER:
            retList = SlotAdapter.checkXdUnloading(vehicle, deviceEvent)
        elif vehicle.getType() == VehicleType.HX_LOADER:
            retList = SlotAdapter.checkHxLoading(vehicle, deviceEvent)
        elif vehicle.getType() == VehicleType.HX_UNLOADER:
            retList = SlotAdapter.checkHxUnloading(vehicle, deviceEvent)

        return retList

    @staticmethod
    def checkXdLoading(vehicle, deviceEvent):
        slotRatio = 3    # capability of one device slot / capability of one vehicle slot = 3
        deviceInfo = deviceEvent.getMachineInfo()   # as str: '1:0'
        deviceData = [int(deviceInfo[0]), int(deviceInfo[2])]  # change to [1, 0]
        deviceLoadNum = sum(deviceData) * slotRatio   # one slot on device , mapped 3 slots on vehicle
        availableVehicleSlotNum = vehicle.getAvailableNum()
        
        # available slot on vehicle is not enough
        if availableVehicleSlotNum < deviceLoadNum:
            SlotAdapter.log.info('no enough passport on vehicle %s' % vehicle.getName())
            return None
        
        availableVehicleSlotIndexList = vehicle.getAvailableIndexList()
        # deviceSlotIndexList = [i for i,x in enumerate(deviceData) if x > 0]
        # actualDeviceSlotIndexList = [x for x in deviceSlotIndexList for i in range(slotRatio)]
        actualDeviceSlotIndexList = [x for x in [i for i,x in enumerate(deviceData) if x > 0] for i in range(slotRatio)]
        actualVehicleSlotIndexList = availableVehicleSlotIndexList[:len(actualDeviceSlotIndexList)]
        ret = [(x, actualDeviceSlotIndexList[i]) for i,x in enumerate(actualVehicleSlotIndexList)]
        print(ret)
        return ret

    @staticmethod
    def checkXdUnloading(vehicle, deviceEvent):
        slotRatio = 1
        deviceInfo = deviceEvent.getMachineInfo()   # as str: '1:0:0:0'
        deviceData = [int(deviceInfo[0])]
        deviceUnloadNum = sum(deviceData) * slotRatio
        availableVehicleSlotNum = vehicle.getAvailableNum()

        if availableVehicleSlotNum < deviceUnloadNum:
            SlotAdapter.log.info('no enough slot on vehicle %s' % vehicle.getName())
            return None

        availableVehicleSlotIndexList = vehicle.getAvailableIndexList()
        actualDeviceSlotIndexList = [x for x in [i for i,x in enumerate(deviceData) if x > 0] for i in range(slotRatio)]
        actualVehicleSlotIndexList = availableVehicleSlotIndexList[:len(actualDeviceSlotIndexList)]
        ret = [(x, actualDeviceSlotIndexList[i]) for i,x in enumerate(actualVehicleSlotIndexList)]
        print(ret)
        return ret
    
    @staticmethod
    def checkHxLoading(vehicle, deviceEvent):
        pass

    @staticmethod
    def checkHxUnloading(vehicle, deviceEvent):
        pass
        


if __name__ == '__main__':
    v = XdUnloaderVehicle('xd')
    v.updateByJsonString('{"available_list":[1,1,1,1,1,1,1,1,1],"status":"ERROR"}')
    de = XDEvent('{         \
    "event_source":0,\
    "event_status":0,\
    "info": "1:0",\
    "machine_code": "JC-8000A-89",\
    "machine_ip":"192.168.0.222",\
    "machine_status": 4,\
    "time": "20180404095212",\
    "version": "1.0"\
    }')
    SlotAdapter.checkout(v,de)