import json
import utils
import accepts
from urllib import request
from trans_order import TransportOrder
from order_sequence_head import OrderSequenceHead

class OrderTask(object):
    '''
    define how to create an order task

    attention: no try-catch in this class
    '''

    def __init__(self, logname = 'order task'):
        '''
        instructor
        '''
        # _log must be defined for the decorator mb_default_catch_exception
        self._log = utils.logger().getLogger(logname)
        self._name = 'order_task_default_name'
        self._task = {
            "sequences" : [],
            "transports" : []
        }


    @utils.mb_default_catch_exception
    @accepts.mb_accepts(str)
    def setName(self, name):
        self._name = name


    @utils.mb_default_catch_exception
    def getName(self):
        return self._name

    @utils.mb_default_catch_exception
    def getOrdersNum(self):
        return len(self._task.get('transports'))
    

    @utils.mb_default_catch_exception
    @accepts.mb_accepts(TransportOrder, int, int)
    def addTransportOrder(self, to, seqIndex = -1, orderIndex = -1):
        '''
        there is at least one transport order in a task
        '''
        if (-1 != seqIndex):
            to.setWrappingSequence(self.getSequenceNameByIndex(seqIndex))

        if (-1 != orderIndex):
            to.addOrderDependencies(self.getOrderNameByIndex(orderIndex))

        self._task.get('transports').append(to.getOrder())



    @utils.mb_default_catch_exception
    @accepts.mb_accepts(OrderSequenceHead)
    def addOrderSequenceHead(self, os):
        '''
        there is at least one order sequence in a task
        '''
        self._task.get('sequences').append(os.getSequence())


    @utils.mb_default_catch_exception
    @accepts.mb_accepts(int)
    def getOrderNameByIndex(self, idx):
        '''
        return an order's name, for dependencies
        '''
        if idx >= 0 and idx < len(self._task.get('transports')):
            return "%s_order_%d" % (self._name, idx)
        else:
            raise IndexError('illegal order index')

        return 'illegal order index'


    @utils.mb_default_catch_exception
    @accepts.mb_accepts(int)
    def getSequenceNameByIndex(self, idx):
        '''
        return an sequence's name, for warpping sequence
        '''
        if idx >= 0 and idx < len(self._task.get('sequences')):
            return "%s_seq_%d" % (self._name, idx)
        else:
            raise IndexError('illegal sequence index')

        return 'illegal sequence index'
        

    @utils.mb_default_catch_exception
    def encode(self):
        '''
        need verify!! use jsonschema TODO
        '''
        return json.dumps(self._task)




if __name__ == '__main__':
    
    t = TransportOrder()