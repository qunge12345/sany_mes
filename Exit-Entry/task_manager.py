
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
from communication_terminal import CommunicationTerminal, ReplyTaskStatus

class TaskManager(object):

    tom = TransportOrderManager(serverIP = "127.0.0.1", serverPort = 55200)

    @staticmethod
    def createNormalTask(evt, vehicle):
        '''
        create a thread of normal task
        '''
        vehicle.setStatus(VehicleStatus.PROCEEDING)
        CommunicationTerminal.typicalSend(evt, ReplyTaskStatus.EXECUTING)

        nt = threading.Thread(target = TaskManager.normalTask, name = 'normal_task_at_%s' % evt.getMachineName(), args = (evt, vehicle))
        nt.setDaemon(True)
        nt.start()

    @staticmethod
    def createReloadTask(vehicle):
        '''
        create a thread of reload task
        '''
        vehicle.setStatus(VehicleStatus.PROCEEDING)

        rt = threading.Thread(target = TaskManager.reloadTask, name = 'reload_task_at_%s' % vehicle.getName(), args = (vehicle,))
        rt.setDaemon(True)
        rt.start()

    @staticmethod
    def normalTask(evt, vehicle):
        '''
        a normal task to load or unload
        '''
        # operation list
        operationList = SlotAdapter.checkout(vehicle, evt)

        while operationList == None:
            TaskManager.reloadTask(vehicle, False)
            operationList = SlotAdapter.checkout(vehicle, evt)

        # sequence head
        sTrans = OrderSequenceHead()
        sTrans.setIntendedVehicle(vehicle.getName())
        sTrans.setFailureFatal(True)
        sArm = OrderSequenceHead()
        sArm.setCategory('ARM_passport')
        sArm.setFailureFatal(True)
        
        # order task
        name = 'normal_at_' + evt.getMachineName() + '_' + vehicle.getName() + \
        '_' + evt.getType().name + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        task = OrderTask()
        task.setName(name)
        task.addOrderSequenceHead(sTrans)
        task.addOrderSequenceHead(sArm)

        # ****difference of vehicle and devices, begin****
        ONE_SIDE_SLOT_NUM = 3
        if vehicle.getType() == VehicleType.XD_LOADER:
            ONE_SIDE_SLOT_NUM = 3
        elif vehicle.getType() == VehicleType.XD_UNLOADER:
            ONE_SIDE_SLOT_NUM = 4
        elif vehicle.getType() in (VehicleType.HX_LOADER, VehicleType.HX_UNLOADER):
            ONE_SIDE_SLOT_NUM = 3

        from_str = 'from'
        to_str = 'to'
        if vehicle.getType() in (VehicleType.XD_UNLOADER, VehicleType.HX_UNLOADER):
            from_str = 'to'
            to_str = 'from'

        depth = ''
        tempI = 0
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

        # wait to inform the production device ??
        t2.addDestination(t1LocName, 'Wait')#, TransportOrder.createProterty('duration', '100'))
        if vehicle.getType() == VehicleType.XD_LOADER:
            tempI = 0
        
        # show if arm has taken picture for marking
        remark = False

        for v in operationList:
            if v[0] < ONE_SIDE_SLOT_NUM:   # the same side

                properties = []

                # take picture for mark
                if False == remark:
                    remark = True
                    properties.append(TransportOrder.createProterty('remark', '0'))

                # special 
                if vehicle.getType() == VehicleType.XD_LOADER:
                    depth = '_' + str(tempI)
                    tempI += 1
                    if tempI == 3:
                        tempI = 0
                
                properties.append(TransportOrder.createProterty(from_str, vehicle.getName() + ':'  + str(v[0])))
                properties.append(TransportOrder.createProterty(to_str,evt.getMachineName() + ':'  + str(v[1]) + depth))
                t2.addDestination(t1LocName, 'Grasp', *properties)

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

        # show if arm has taken picture for marking
        remark = False

        for v in operationList:
            if v[0] >= ONE_SIDE_SLOT_NUM:   #   the same side

                properties = []

                # take picture for mark
                if False == remark:
                    remark = True
                    properties.append(TransportOrder.createProterty('remark', '1'))

                # sepcial
                if vehicle.getType() == VehicleType.XD_LOADER:
                    depth = '_' + str(tempI)
                    tempI += 1
                    if tempI == 3:
                        tempI = 0
                properties.append(TransportOrder.createProterty(from_str, vehicle.getName() + ':'  + str(v[0])))
                properties.append(TransportOrder.createProterty(to_str,evt.getMachineName() + ':'  + str(v[1]) + depth))
                t4.addDestination(t1LocName, 'Grasp', *properties)

        t5 = TransportOrder()   # vehicle, depend t4
        t5.addDestination(t0LocName, 'Wait', TransportOrder.createProterty('orientation', str(orientation)))

        task.addTransportOrder(t0, 0)
        task.addTransportOrder(t1, 1)
        task.addTransportOrder(t2, 1, 0)
        task.addTransportOrder(t3, 0, 2)
        task.addTransportOrder(t4, 1, 3)
        task.addTransportOrder(t5, 0, 4)

        TaskManager.tom.sendOrderTask(task)
        CommunicationTerminal.typicalSend(evt, ReplyTaskStatus.GRASPING)

        time.sleep(10)
        # check 
        orderState = TaskManager.getOrderTaskState(name)
        while orderState not in ('FINISHED', 'FAILED'):
            time.sleep(2)
            orderState = TaskManager.getOrderTaskState(name)

        if orderState == 'FINISHED':
            CommunicationTerminal.typicalSend(evt, ReplyTaskStatus.SUCCESS)
        elif orderState == 'FAILED':
            CommunicationTerminal.typicalSend(evt, ReplyTaskStatus.FAILED)


        vehicle.setStatus(VehicleStatus.IDLE)

    @staticmethod
    def reloadTask(vehicle, independent = True):
        '''
        go to reload

        TODO: use config file instead of those string !!!
        '''

        # confirm the location
        location = 'Location_Unload'
        if vehicle.getType() in (VehicleType.XD_LOADER, VehicleType.HX_LOADER):
            location = 'Location_Load'

        t = TransportOrder()
        t.setIntendedVehicle(vehicle.getName())
        leftDoorDI = '14'
        rightDoorDI = '15'
        t.addDestination('Location_WD_Left', 'SetDO', TransportOrder.createProterty(leftDoorDI, 'true'))
        t.addDestination('Location_WD_Left', 'Wait', TransportOrder.createProterty('duration', '2000'))
        t.addDestination('Location_WD_Inside', 'SetDO', TransportOrder.createProterty(leftDoorDI, 'false'))
        t.addDestination('Location_WD_Inside', 'Wait', TransportOrder.createProterty('duration', '5000'))
        t.addDestination('Location_WD_Inside', 'SetDO', TransportOrder.createProterty(rightDoorDI, 'true'))
        t.addDestination('Location_WD_Inside', 'Wait', TransportOrder.createProterty('duration', '2000'))
        t.addDestination('Location_WD_Right', 'SetDO', TransportOrder.createProterty(rightDoorDI, 'false'))
        t.addDestination(location, 'Wait', TransportOrder.createProterty('duration', '10000'))
        t.addDestination('Location_WD_Right', 'SetDO', TransportOrder.createProterty(rightDoorDI, 'true'))
        t.addDestination('Location_WD_Right', 'Wait', TransportOrder.createProterty('duration', '2000'))
        t.addDestination('Location_WD_Inside', 'SetDO', TransportOrder.createProterty(rightDoorDI, 'false'))
        t.addDestination('Location_WD_Inside', 'Wait', TransportOrder.createProterty('duration', '5000'))
        t.addDestination('Location_WD_Inside', 'SetDO', TransportOrder.createProterty(leftDoorDI, 'true'))
        t.addDestination('Location_WD_Inside', 'Wait', TransportOrder.createProterty('duration', '2000'))
        t.addDestination('Location_WD_Left', 'SetDO', TransportOrder.createProterty(leftDoorDI, 'false'))

        name = 'reload_' + vehicle.getName() + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        TaskManager.tom.sendOrder(t, name)

        # wait for executing
        time.sleep(10)

        orderState = TaskManager.getOrderState(name)
        while orderState not in ('FINISHED', 'FAILED'):
            time.sleep(5)
            orderState = TaskManager.getOrderState(name)

        if orderState == 'FINISHED':
            pass
        elif orderState == 'FAILED':
            pass

        if independent == True:
            vehicle.setStatus(VehicleStatus.IDLE)

    @staticmethod
    def getOrderState(orderName):
        '''
        return True if order is finished
        '''
        return TaskManager.tom.getOrderInfo(orderName).get('state')

    @staticmethod
    def getOrderTaskState(orderTask):
        '''
        return True if order task is finished
        '''
        return TaskManager.tom.getOrderInfo(orderTask.getOrderNameByIndex(orderTask.getOrdersNum() - 1)).get('state')

if __name__ == '__main__':
    xdv = XdLoaderVehicle('xiongdiloader')
    xdv.updateByInfo({"DI":[True,False,True,True,True,True,True,True,True,True],"status":"ERROR"})

    de = XDEvent('{         \
    "event_source":"0",\
    "event_status":0,\
    "info": "3",\
    "machine_code": "JC-8000A-89",\
    "machine_ip":"192.168.0.222",\
    "machine_status": "4",\
    "time": "20180404095212",\
    "version": "1.0"\
    }')
    TaskManager.createNormalTask(de, xdv)
    # TaskManager.createReloadTask(xdv)
    time.sleep(5)