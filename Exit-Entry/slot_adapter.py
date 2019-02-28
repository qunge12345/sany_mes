import sys
sys.path.append('..')
sys.path.append('.')
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
        return a list of available pairs, or None
        
        the format of list is : [(vehicle_slot_i, device_slot_i),...]
        '''
        retList = []

        # type mismatch
        if vehicle.getType().value != deviceEvent.getType().value:
            if vehicle.getType() == VehicleType.HX_TRANS and deviceEvent.getType() in (DeviceType.HX_LOAD, DeviceType.HX_UNLOAD):
                pass
            else:
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
        elif vehicle.getType() == VehicleType.HX_TRANS:
            if DeviceType.HX_LOAD == deviceEvent.getType():
                retList = SlotAdapter.checkHxLoading(vehicle, deviceEvent)
            elif DeviceType.HX_UNLOAD == deviceEvent.getType():
                retList = SlotAdapter.checkHxUnloading(vehicle, deviceEvent)

        return retList


    @staticmethod
    def checkRequirement(deviceEvent):
        deviceData = []
        if deviceEvent.getType() == DeviceType.XD_LOAD:
            slotRatio = 3    # capability of one device slot / capability of one vehicle slot = 3
            deviceInfo = deviceEvent.getMachineInfo()   # as str: '1:0'
            deviceData = [int(deviceInfo) & 1, (int(deviceInfo) >> 1) & 1]   # change to [1, 0]
        elif deviceEvent.getType() == DeviceType.XD_UNLOAD:
            slotRatio = 1
            deviceInfo = deviceEvent.getMachineInfo()   # as str: '1:0:0:0'
            deviceData = [int(deviceInfo) & 1]
        
        return deviceData

    @staticmethod
    def checkXdLoading(vehicle, deviceEvent):
        deviceInfo = deviceEvent.getMachineInfo()   # as str: '2:3:0:1'
        deviceData = list(map(int, deviceInfo.split(':')))
        deviceData = list(map(lambda x: x if x <= 3 else 3, deviceData))
        deviceLoadNum = sum(deviceData)   # one slot on device , mapped 3 slots on vehicle
        availableVehicleSlotNum = vehicle.getAvailableNum()
        
        # available slot on vehicle is not enough
        if availableVehicleSlotNum < deviceLoadNum:
            SlotAdapter.log.info('no enough passport on vehicle %s' % vehicle.getName())
            return None
        
        availableVehicleSlotIndexList = vehicle.getAvailableIndexList()
        actualDeviceSlotIndexList = [x for x in [i for i,x in enumerate(deviceData) if x > 0] for i in range(deviceData[x])]
        actualVehicleSlotIndexList = availableVehicleSlotIndexList[:len(actualDeviceSlotIndexList)]
        ret = [(x, actualDeviceSlotIndexList[i]) for i,x in enumerate(actualVehicleSlotIndexList)]
        print(ret)
        return ret
    
    # @staticmethod
    # def checkXdLoading(vehicle, deviceEvent):
    #     slotRatio = 3    # capability of one device slot / capability of one vehicle slot = 3
    #     deviceInfo = deviceEvent.getMachineInfo()   # as str: '3'
    #     deviceData = [int(deviceInfo) & 1, (int(deviceInfo) >> 1) & 1]   # change to [1, 0] 
    #     deviceLoadNum = sum(deviceData) * slotRatio   # one slot on device , mapped 3 slots on vehicle
    #     availableVehicleSlotNum = vehicle.getAvailableNum()
        
    #     # available slot on vehicle is not enough
    #     if availableVehicleSlotNum < deviceLoadNum:
    #         SlotAdapter.log.info('no enough passport on vehicle %s' % vehicle.getName())
    #         return None
        
    #     availableVehicleSlotIndexList = vehicle.getAvailableIndexList()
    #     # deviceSlotIndexList = [i for i,x in enumerate(deviceData) if x > 0]
    #     # actualDeviceSlotIndexList = [x for x in deviceSlotIndexList for i in range(slotRatio)]
    #     actualDeviceSlotIndexList = [x for x in [i for i,x in enumerate(deviceData) if x > 0] for i in range(slotRatio)]
    #     actualVehicleSlotIndexList = availableVehicleSlotIndexList[:len(actualDeviceSlotIndexList)]
    #     ret = [(x, actualDeviceSlotIndexList[i]) for i,x in enumerate(actualVehicleSlotIndexList)]
    #     print(ret)
    #     return ret

    @staticmethod
    def checkXdUnloading(vehicle, deviceEvent):
        slotRatio = 1
        deviceInfo = deviceEvent.getMachineInfo()   # as str: '1:0:0:0'
        deviceData = list(map(lambda x: 1 if int(x) > 0 else 0, deviceInfo.split(':')))
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
        deviceInfo = deviceEvent.getMachineInfo()   # as '120' or '80'
        deviceLoadNum = int(deviceInfo) // 40
        deviceLoadNum = deviceLoadNum if deviceLoadNum <= 3 else 3
        deviceData = [0 for i in range(deviceLoadNum)]

        availableVehicleSlotNum = 0
        if VehicleType.HX_LOADER == vehicle.getType():
            availableVehicleSlotNum = vehicle.getAvailableNum()
        elif VehicleType.HX_TRANS == vehicle.getType():
            availableVehicleSlotNum = vehicle.getLoaderAvailableNum()

        # available slot on vehicle is not enough
        if availableVehicleSlotNum < deviceLoadNum:
            SlotAdapter.log.info('no enough card on vehicle %s' % vehicle.getName())
            return None

        availableVehicleSlotIndexList = []
        if VehicleType.HX_TRANS == vehicle.getType():
            availableVehicleSlotIndexList = vehicle.getLoaderAvailableIndexList()
        else:
            availableVehicleSlotIndexList = vehicle.getAvailableIndexList()

        actualDeviceSlotIndexList = deviceData
        actualVehicleSlotIndexList = availableVehicleSlotIndexList[:len(actualDeviceSlotIndexList)]
        ret = [(x, actualDeviceSlotIndexList[i]) for i,x in enumerate(actualVehicleSlotIndexList)]
        print(ret)
        return ret

        
    @staticmethod
    def checkHxUnloading(vehicle, deviceEvent):
        slotRatio = 1
        deviceInfo = deviceEvent.getMachineInfo()   # as str: '1:0:0:0'
        deviceData = list(map(int, deviceInfo.split(':')))
        deviceUnloadNum = sum(deviceData) * slotRatio
        
        availableVehicleSlotNum = 0
        if VehicleType.HX_UNLOADER == vehicle.getType():
            availableVehicleSlotNum = vehicle.getAvailableNum()
        elif VehicleType.HX_TRANS == vehicle.getType():
            availableVehicleSlotNum = vehicle.getUnloaderAvailableNum()

        if availableVehicleSlotNum < deviceUnloadNum:
            SlotAdapter.log.info('no enough slot on vehicle %s' % vehicle.getName())
            return None

        availableVehicleSlotIndexList = []
        if VehicleType.HX_TRANS == vehicle.getType():
            availableVehicleSlotIndexList = vehicle.getUnloaderAvailableIndexList()
        else:
            availableVehicleSlotIndexList = vehicle.getAvailableIndexList()

        actualDeviceSlotIndexList = [x for x in [i for i,x in enumerate(deviceData) if x > 0] for i in range(slotRatio)]
        actualVehicleSlotIndexList = availableVehicleSlotIndexList[:len(actualDeviceSlotIndexList)]
        ret = [(x, actualDeviceSlotIndexList[i]) for i,x in enumerate(actualVehicleSlotIndexList)]
        print(ret)
        return ret
        


if __name__ == '__main__':
    xdv = XdUnloaderVehicle('xd')
    xdv.updateByInfo({"DI":[True,False,True,True,False,False,True,False,True,True,False,False,True,False,True,True,False,False,True,False,True,True,False,False,True,False,True,True,False,False,True,True,True,True],"status":1})
    de = XDEvent('{         \
    "event_source":"0",\
    "event_status":"0",\
    "info": "1:1110:1",\
    "machine_code": "JC-8000A-89",\
    "machine_ip":"192.168.0.222",\
    "machine_status": "5",\
    "time": "20180404095212",\
    "token":"asdfasdf",\
    "version": "1.0"\
    }')
    SlotAdapter.checkout(xdv,de)