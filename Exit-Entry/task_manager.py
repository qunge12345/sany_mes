
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

from trans_order import TransportOrder
from order_sequence_head import OrderSequenceHead
from order_task import OrderTask
from trans_order_manager import TransportOrderManager

class TaskManager(object):

    tom = TransportOrderManager(serverIP = "127.0.0.1", serverPort = 55200)

    @staticmethod
    def createNormalTask(evt, vehicle):
        '''
        create a thread of normal task
        '''
        nt = threading.Thread(target = TaskManager.normalTask, name = 'normal_task_at_%s' % evt.getMachineName(), args = (evt, vehicle))
        nt.setDaemon(True)
        nt.start()

    @staticmethod
    def createReloadTask(vehicle):
        '''
        create a thread of reload task
        '''
        rt = threading.Thread(target = TaskManager.reloadTask, name = 'reload_task_at_%s' % vehicle.getName(), args = (vehicle,))
        rt.setDaemon(True)
        rt.start()

    @staticmethod
    def normalTask(evt, vehicle):
        '''
        a normal task to load or unload
        '''
        vehicle.setStatus(VehicleStatus.PROCEEDING)

        # sequence head
        sTrans = OrderSequenceHead()
        sTrans.setIntendedVehicle(vehicle.getName())
        sTrans.setFailureFatal(False)
        sArm = OrderSequenceHead()
        sArm.setCategory('ARM_passport')
        sArm.setFailureFatal(False)
        
        # order task
        name = 'normal_at_' + evt.getMachineName() + '_' + vehicle.getName() \
        '_' + evt.getType().name + '_' + datetime.datetime.now() 
        task = OrderTask()
        task.setName(name)
        task.addOrderSequenceHead(sTrans)
        task.addOrderSequenceHead(sArm)
        # operation list
        operationList = SlotAdapter.checkout(vehicle, evt)

        # ****difference of vehicle and devices, begin****
        ONE_SIDE_SLOT_NUM = 3
        if vehicle.getType() in (VehicleType.XD_LOADER, VehicleType.XD_UNLOADER):
            ONE_SIDE_SLOT_NUM = 3
        elif evt.getType() in (VehicleType.HX_LOADER, VehicleType.HX_UNLOADER):
            ONE_SIDE_SLOT_NUM = 3

        from_str = 'from'
        to_str = 'to'
        if vehicle.getType() in (VehicleType.XD_UNLOADER, VehicleType.HX_UNLOADER):
            from_str = 'to'
            to_str = 'from'
        # ****difference of vehicle and devices, end****

        # transport order
        t0 = TransportOrder()   # vehicle
        t0LocName = 'Location_' + evt.getMachineName() + '_' + evt.getType().name + '_Transport'
        t0.addDestination(t0LocName, 'Wait')

        t1 = TransportOrder()   # arm
        t1LocName = 'Location_' + evt.getMachineName() + '_' + evt.getType().name + '_Arm'
        t1.addDestination(t1LocName, 'Wait')

        # TELL THE DEVICE , START TO GRASP
        # TODO  !! let ARM_VEHICLE to do this?

        t2 = TransportOrder()   # arm, depend t0
        t2.addDestination(t1LocName, 'Wait')
        for v in operationList:
            if v[0] < ONE_SIDE_SLOT_NUM:   #   0,1,2 are the same side !!! this param will be extracted TODO
                t2.addDestination(t1LocName, 'Grasp', TransportOrder.createProterty(from_str, 'self_' + v[0]), \
                TransportOrder.createProterty(to_str,'device_' + v[1]))

        t3 = TransportOrder()   # vehicle, depend t2
        needTurn = False
        orientation = 0
        for v in operationList:
            if v[0] >= ONE_SIDE_SLOT_NUM:
                needTurn = True
                break
        if needTurn:
            orientation = 180
        t3.addDestination(t0LocName, 'Wait', TransportOrder.createProterty('orientation', str(orientation)))

        t4 = TransportOrder()   # arm, depend t3
        t4.addDestination(t1LocName, 'Wait')
        for v in operationList:
            if v[0] >= ONE_SIDE_SLOT_NUM:   #   0,1,2 are the same side !!! this param will be extracted TODO
                t4.addDestination(t1LocName, 'Grasp', TransportOrder.createProterty(from_str, 'self_' + v[0]), \
                TransportOrder.createProterty(to_str,'device_' + v[1]))

        t5 = TransportOrder()   # vehicle, depend t4
        t5.addDestination(t0LocName, 'Wait', TransportOrder.createProterty('orientation', str(orientation)))

        task.addTransportOrder(t0, 0)
        task.addTransportOrder(t1, 1)
        task.addTransportOrder(t2, 1, 0)
        task.addTransportOrder(t3, 0, 2)
        task.addTransportOrder(t4, 1, 3)
        task.addTransportOrder(t5, 0, 4)

        tom.sendOrderTask(task)
        # check 
        while False == TaskManager.isOrderTaskFinished(task):
            time.sleep(5)

        # TELL THE DEVICE , GRASP OVER !! TODO

        vehicle.setStatus(VehicleStatus.IDLE)

    @staticmethod
    def reloadTask(vehicle):
        '''
        go to reload

        TODO: use config file instead of those string !!!
        '''
        vehicle.setStatus(VehicleStatus.PROCEEDING)

        # confirm the location
        location = 'Location_Unload'
        if vehicle.getType() in (VehicleType.XD_LOADER, VehicleType.HX_LOADER):
            location = 'Location_Load'

        t = TransportOrder()
        t.setIntendedVehicle(vehicle.getName())
        prop = TransportOrder.createProterty('duration', '5000')
        t.addDestination(location, 'Wait', *(prop,))
        name = 'reload_' + vehicle.getName() + '_' + datetime.datetime.now()
        tom.sendOrder(t, name)

        # wait for executing
        time.sleep(10)

        while False == TaskManager.isOrderFinished(name):
            time.sleep(5)

        vehicle.setStatus(VehicleStatus.IDLE)

    @staticmethod
    def isOrderFinished(orderName):
        '''
        return True if order is finished
        '''
        orderStatus = tom.getOrderInfo(orderName)['state']
        return orderStatus in ('FINISHED', 'FAILED')

    @staticmethod
    def isOrderTaskFinished(orderTask):
        '''
        return True if order task is finished
        '''
        orderStatus = tom.getOrderInfo(orderTask.getOrderNameByIndex(orderTask.getOrdersNum() - 1))['state']
        return orderStatus in ('FINISHED', 'FAILED')

if __name__ == '__main__':
    pass