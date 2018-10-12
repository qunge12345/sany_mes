
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

    tom = TransportOrderManager()

    @staticmethod
    def createWork(evt, vehicle):
        pass

    @staticmethod
    def createReload(vehicle):
        '''
        go to reload location
        '''


    @staticmethod
    def isOrderTaskFinished(orderTaskName):
        pass

