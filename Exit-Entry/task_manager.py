
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
from replyer import Replyer, ReplyTaskStatus

class TaskManager(object):

    tom = TransportOrderManager(serverIP = "192.168.2.100", serverPort = 55200)
    log = utils.logger().getLogger('task manager')

    @staticmethod
    def createNormalTask(evt, vehicle):
        '''
        create a thread of normal task
        '''
        TaskManager.log.info('normal task created: ' + str(evt) + ' --- ' + str(vehicle))
        vehicle.setState(VehicleState.PROCEEDING)
        Replyer.typicalSend(evt, ReplyTaskStatus.EXECUTING)

        thisFunc = TaskManager.normalXdTask
        if evt.getType() in (DeviceType.HX_LOAD, DeviceType.HX_UNLOAD):
            thisFunc = TaskManager.normalHxTask

        nt = threading.Thread(target = thisFunc, name = 'normal_task_at_%s' % evt.getMachineName(), args = (evt, vehicle))
        nt.setDaemon(True)
        nt.start()

    @staticmethod
    def createReloadTask(vehicle):
        '''
        create a thread of reload task
        '''
        TaskManager.log.info('reload task created: ' + str(vehicle))
        vehicle.setState(VehicleState.PROCEEDING)

        rt = threading.Thread(target = TaskManager.reloadTask, name = 'reload_task_at_%s' % vehicle.getName(), args = (vehicle,))
        rt.setDaemon(True)
        rt.start()

    @staticmethod
    def createDropTask(vehicle):
        '''
        create a thread of drop task
        '''
        TaskManager.log.info('drop task created: ' + str(vehicle))
        vehicle.setState(VehicleState.PROCEEDING)

        dt = threading.Thread(target = TaskManager.dropTask, name = 'drop_task_at_%s' % vehicle.getName(), args = (vehicle,))
        dt.setDaemon(True)
        dt.start()



    @staticmethod
    def normalXdTask(evt, vehicle):
        '''
        a normal xiongdi task to load or unload
        '''
        # operation list
        operationList = SlotAdapter.checkout(vehicle, evt)

        while operationList == None:
            if evt.getType() == DeviceType.XD_LOAD:
                TaskManager.reloadTask(vehicle, False)
            else:
                TaskManager.dropTask(vehicle, False)
            operationList = SlotAdapter.checkout(vehicle, evt)

        # sequence head
        sTrans = OrderSequenceHead()
        sTrans.setIntendedVehicle(vehicle.getName())
        sTrans.setFailureFatal(True)
        sArm = OrderSequenceHead()
        sArm.setCategory('ARM_passport')
        sArm.setFailureFatal(True)
        
        # order task
        name = 'normal_xd_at_' + evt.getMachineName() + '_' + vehicle.getName() + \
        '_' + evt.getType().name + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        task = OrderTask()
        task.setName(name)
        task.addOrderSequenceHead(sTrans)
        task.addOrderSequenceHead(sArm)

        # ****difference of vehicle and devices, begin****
        ONE_SIDE_SLOT_NUM = 3
        if vehicle.getType() == VehicleType.XD_LOADER:
            ONE_SIDE_SLOT_NUM = 6
        elif vehicle.getType() == VehicleType.XD_UNLOADER:
            ONE_SIDE_SLOT_NUM = 3

        from_str = 'from'
        to_str = 'to'
        operation = 'GraspLoad'
        if vehicle.getType() in (VehicleType.XD_UNLOADER, ):
            from_str = 'to'
            to_str = 'from'
            operation = 'GraspUnload'

        depth = ':0'
        tempI = 0
        # ****difference of vehicle and devices, end****

        # transport order
        t0 = TransportOrder()   # vehicle
        t0LocName = 'Location_' + evt.getMachineName() + '_' + evt.getType().name + '_Transport'
        t0.addDestination(t0LocName, 'Wait')

        t1 = TransportOrder()   # arm
        t1LocName = 'Location_' + evt.getMachineName() + '_' + evt.getType().name + '_Arm'
        t1.addDestination(t1LocName, 'Wait')

        t2 = TransportOrder()   # arm, depend t0
        # wait to inform the production device ??
        t2.addDestination(t1LocName, 'ArmReset')#, TransportOrder.createProterty('duration', '100'))
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
                    depth = ':' + str(tempI)
                    tempI += 1
                    if tempI == 3:
                        tempI = 0
                
                properties.append(TransportOrder.createProterty(from_str, str(v[0] + 1)))
                properties.append(TransportOrder.createProterty(to_str, evt.getMachineName()[-2:] + ':' + str(v[1]) + depth))
                t2.addDestination(t1LocName, operation, *properties)

        t3 = TransportOrder()   # vehicle, depend t2
        needTurn = False
        inverse_angle = 'false'
        for v in operationList:
            if v[0] >= ONE_SIDE_SLOT_NUM:
                needTurn = True
                break
        if needTurn:
            inverse_angle = 'true'
        t3.addDestination(t0LocName, 'Wait', TransportOrder.createProterty('inverse_angle', inverse_angle))

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
                    depth = ':' + str(tempI)
                    tempI += 1
                    if tempI == 3:
                        tempI = 0
                properties.append(TransportOrder.createProterty(from_str, str(v[0] + 1)))
                properties.append(TransportOrder.createProterty(to_str, evt.getMachineName()[-2:] + ':' + str(v[1]) + depth))
                t4.addDestination(t1LocName, operation, *properties)

        t4.addDestination(t1LocName, 'ArmReset')
        t5 = TransportOrder()   # vehicle, depend t4
        t5.addDestination(t0LocName, 'Wait', TransportOrder.createProterty('inverse_angle', inverse_angle))
        t6 = TransportOrder()   # arm, depend t5
        t6.addDestination(t1LocName, 'Wait')

        task.addTransportOrder(t0, 0)
        task.addTransportOrder(t1, 1)
        task.addTransportOrder(t2, 1, 0)
        task.addTransportOrder(t3, 0, 2)
        task.addTransportOrder(t4, 1, 3)
        task.addTransportOrder(t5, 0, 4)
        task.addTransportOrder(t6, 1, 5)

        try:
            TaskManager.tom.sendOrderTask(task)

            time.sleep(5)
            # check
            sendGrasping = False
            orderState = TaskManager.getOrderTaskState(task)
            while orderState not in ('FINISHED', 'FAILED'):
                time.sleep(1.5)
                orderState = TaskManager.getOrderTaskState(task)
                time.sleep(0.5)
                if False == sendGrasping:
                    if True == TaskManager.isGraspStart(task):
                        sendGrasping = True
                        Replyer.typicalSend(evt, ReplyTaskStatus.GRASPING)



            if orderState == 'FINISHED':
                Replyer.typicalSend(evt, ReplyTaskStatus.SUCCESS)
            elif orderState == 'FAILED':
                Replyer.typicalSend(evt, ReplyTaskStatus.FAILED)
        except Exception as e:
            TaskManager.log.error(e)
        finally:
            vehicle.setState(VehicleState.IDLE)
            TaskManager.log.info('normal task over: ' + vehicle.getName() + ' : ' + str(evt) )

    @staticmethod
    def normalHxTask(evt, vehicle):
        '''
        a normal hangxin task to load or unload
        '''
        # operation list
        operationList = SlotAdapter.checkout(vehicle, evt)

        while operationList == None:
            if evt.getType() == DeviceType.HX_LOAD:
                TaskManager.reloadTask(vehicle, False)
            else:
                TaskManager.dropTask(vehicle, False)
            operationList = SlotAdapter.checkout(vehicle, evt)

        # sequence head
        sTrans = OrderSequenceHead()
        sTrans.setIntendedVehicle(vehicle.getName())
        sTrans.setFailureFatal(True)
        sArm = OrderSequenceHead()
        sArm.setCategory('ARM_card')
        sArm.setFailureFatal(True)
        
        # order task
        name = 'normal_hx_at_' + evt.getMachineName() + '_' + vehicle.getName() + \
        '_' + evt.getType().name + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        task = OrderTask()
        task.setName(name)
        task.addOrderSequenceHead(sTrans)
        task.addOrderSequenceHead(sArm)

        # ****difference of vehicle and devices, begin****
        from_str = 'from'
        to_str = 'to'
        operation = 'GraspLoad'
        if evt.getType() == DeviceType.HX_UNLOAD:
            from_str = 'to'
            to_str = 'from'
            operation = 'GraspUnload'

        depth = ':0'
        tempI = 1
        # ****difference of vehicle and devices, end****

        # transport order
        t0 = TransportOrder()   # vehicle
        t0LocName = 'Location_' + evt.getMachineName() + '_' + evt.getType().name + '_Transport'
        t0.addDestination(t0LocName, 'Wait')

        t1 = TransportOrder()   # arm
        t1LocName = 'Location_' + evt.getMachineName() + '_' + evt.getType().name + '_Arm'
        t1.addDestination(t1LocName, 'Wait')

        t2 = TransportOrder()   # arm, depend t0
        # wait to inform the production device ??
        t2.addDestination(t1LocName, 'ArmReset')#, TransportOrder.createProterty('duration', '100'))
        if evt.getType() == DeviceType.HX_LOAD:
            tempI = 1
        
        # show if arm has taken picture for marking
        remark = False

        for v in operationList:
            properties = []

            # take picture for mark
            if False == remark:
                remark = True
            
            properties.append(TransportOrder.createProterty('remark', '0'))

            # special 
            if evt.getType() == DeviceType.HX_LOAD:
                depth = ':' + str(tempI)
                tempI += 1
                if tempI == 4:
                    tempI = 1
            
            properties.append(TransportOrder.createProterty(from_str, str(v[0] + 1)))
            properties.append(TransportOrder.createProterty(to_str, evt.getMachineName()[-2:] + ':' + str(v[1] + 1) + depth))
            t2.addDestination(t1LocName, operation, *properties)

        t2.addDestination(t1LocName, 'ArmReset')
        t3 = TransportOrder()   # vehicle, depend t4
        t3.addDestination(t0LocName, 'Wait')
        t4 = TransportOrder()   # arm, depend t5
        t4.addDestination(t1LocName, 'Wait')

        task.addTransportOrder(t0, 0)
        task.addTransportOrder(t1, 1)
        task.addTransportOrder(t2, 1, 0)
        task.addTransportOrder(t3, 0, 2)
        task.addTransportOrder(t4, 1, 3)

        try:
            TaskManager.tom.sendOrderTask(task)

            time.sleep(5)
            # check
            sendGrasping = False
            orderState = TaskManager.getOrderTaskState(task)
            while orderState not in ('FINISHED', 'FAILED'):
                time.sleep(1.5)
                orderState = TaskManager.getOrderTaskState(task)
                time.sleep(0.5)
                if False == sendGrasping:
                    if True == TaskManager.isGraspStart(task):
                        sendGrasping = True
                        Replyer.typicalSend(evt, ReplyTaskStatus.GRASPING)

            if orderState == 'FINISHED':
                Replyer.typicalSend(evt, ReplyTaskStatus.SUCCESS)
            elif orderState == 'FAILED':
                Replyer.typicalSend(evt, ReplyTaskStatus.FAILED)
        except Exception as e:
            TaskManager.log.error(e)
        finally:
            vehicle.setState(VehicleState.IDLE)
            TaskManager.log.info('normal task over: ' + vehicle.getName() + ' : ' + str(evt) )

    @staticmethod
    def reloadTask(vehicle, independent = True):
        '''
        go to reload

        TODO: use config file instead of those string !!!
        '''

        # confirm the location
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
        t.addDestination(location, 'WaitKey', TransportOrder.createProterty('1', '1'))
        t.addDestination('Location_WD_Right', 'SetDO', TransportOrder.createProterty(rightDoorDI, 'true'))
        t.addDestination('Location_WD_Right', 'Wait', TransportOrder.createProterty('duration', '2000'))
        t.addDestination('Location_WD_Inside', 'SetDO', TransportOrder.createProterty(rightDoorDI, 'false'))
        t.addDestination('Location_WD_Inside', 'Wait', TransportOrder.createProterty('duration', '5000'))
        t.addDestination('Location_WD_Inside', 'SetDO', TransportOrder.createProterty(leftDoorDI, 'true'))
        t.addDestination('Location_WD_Inside', 'Wait', TransportOrder.createProterty('duration', '2000'))
        t.addDestination('Location_WD_Left', 'SetDO', TransportOrder.createProterty(leftDoorDI, 'false'))

        name = 'reload_' + vehicle.getName() + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

        try:
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
        except Exception as e:
            TaskManager.log.error(e)
        finally:
            if independent == True:
                vehicle.setState(VehicleState.IDLE)
                TaskManager.log.info('reload task over: ' + vehicle.getName())


    @staticmethod
    def dropTask(vehicle, independent = True):
        '''
        go to drop

        TODO: use config file instead of those string !!!
        '''

        # confirm the location
        dev = 'XD'
        if vehicle.getType() == VehicleType.HX_TRANS:
            dev = 'HX'
        location = 'Location_Check_' + dev

        t = TransportOrder()
        t.setIntendedVehicle(vehicle.getName())        
        t.addDestination(location, 'WaitKey', TransportOrder.createProterty('1', '1'))
    
        name = 'check_' + vehicle.getName() + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        try:
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
        except Exception as e:
            TaskManager.log.error(e)
        finally:
            if independent == True:
                vehicle.setState(VehicleState.IDLE)
                TaskManager.log.info('drop task over: ' + vehicle.getName())

    @staticmethod
    def getOrderState(orderName):
        '''
        return True if order is finished
        '''
        return TaskManager.tom.getOrderInfo(orderName).get('state')

    @staticmethod
    def isGraspStart(orderTask):
        '''
        return is the grasp action is started
        '''
        state_0 = TaskManager.tom.getOrderInfo(orderTask.getOrderNameByIndex(0)).get('state')
        state_1 = TaskManager.tom.getOrderInfo(orderTask.getOrderNameByIndex(1)).get('state')
        return True if state_0 in ('FINISHED',) and state_1 in ('FINISHED',) else False

    @staticmethod
    def getOrderTaskState(orderTask):
        '''
        return True if order task is finished
        '''
        return TaskManager.tom.getOrderInfo(orderTask.getOrderNameByIndex(orderTask.getOrdersNum() - 1)).get('state')

if __name__ == '__main__':
    xdv = XdLoaderVehicle('Carrier_XdLoaderVehicle_1')
    xdv.updateByInfo({"DI":[True,False,True,True,False,True,True,True,True,True],"status":"ERROR"})

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