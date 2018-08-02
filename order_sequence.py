import utils
import accepts

import datetime
import json
from trans_order import TransportOrder

class OrderSequence(object):
    '''
    define how to create an order sequence

    attention: no try-catch in this class
    '''

    def __init__(self, logname = 'order sequence'):
        '''
        instructor
        '''
        # _log must be defined for the decorator mb_default_catch_exception
        self._log = utils.logger().getLogger(logname)
        self._sequence = {
            "transports" : [],
            "properties" : []

        }


    @utils.mb_default_catch_exception
    @accepts.mb_accepts(str)
    def setIntendedVehicle(self, vehicle = "undefine_vehicle"):
        '''
        intended vehicle is optional
        '''
        self._sequence["intendedVehicle"] = vehicle

    @utils.mb_default_catch_exception
    @accepts.mb_accepts(str)
    def setCategory(self, category = "-"):
        '''
        order sequence's category is optional
        '''
        self._sequence["category"] = category

    @utils.mb_default_catch_exception
    @accepts.mb_accepts(bool)
    def setFailureFatal(self, failureFatal = True):
        '''
        order sequence's failureFatal is optional
        '''
        self._sequence["failureFatal"] = failureFatal

    
    @utils.mb_default_catch_exception
    @accepts.mb_accepts(TransportOrder)
    def addTransportOrder(self, to):
        '''
        there is at least one transport order in a sequence
        '''
        self._sequence.get('transports').append(to.getOrder())

    @utils.mb_default_catch_exception
    def addProperties(self, *properties):
        '''
        add order sequence properties. this is optional
        '''
        if True == OrderSequence._checkProperties(properties):
            self._sequence.get("properties").extend(properties)
        else:
            self._log.info("wrong order properties with " + str(properties))


    @staticmethod
    @accepts.accepts(str, str)
    def createProterty(key = "undefine", value = ""):
        '''
        create a proterty with specified format
        '''
        return { "key" : key, "value" : value}

    @staticmethod
    @accepts.accepts(tuple)
    def _checkProperties(properties):
        for item in properties:
            if 'key' in item.keys() and 'value' in item.keys():
                if isinstance(item['key'], str) and isinstance(item['value'], str):
                    continue
            return False
        return True
        

    def encode(self):
        '''
        need verify!! use jsonschema TODO
        '''
        return json.dumps(self._sequence)




if __name__ == '__main__':
    
    t = TransportOrder()
    li = ({
    "key" : "transport order-specific key",
    "value" : "some value"
    },{
        "key" : "sssssssssss key",
        "value" : "some value"
    })
    t.addDestination("aaa","hahahaha",*li)
    t.addDestination("bbb","babababa")

    t1 = TransportOrder()
    t1.addDestination("ccc","babababa")
    t1.addDestination("ddd","babababa")
    t1.addOrderDependencies('pppppppppp', 'ssssssssssss')

    s = OrderSequence()
    s.addTransportOrder(t)
    s.addTransportOrder(t1)
    s.setCategory('fuck')

    print(s.encode())