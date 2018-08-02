import utils
import accepts

import datetime
import json

class TransportOrder(object):
    '''
    define how to create a transport order

    attention: no try-catch in this class
    '''

    def __init__(self, logname = 'transport order'):
        '''
        instructor
        '''
        # _log must be defined for the decorator mb_default_catch_exception
        self._log = utils.logger().getLogger(logname)
        self._order = {
            "deadline"      : (datetime.datetime.now() + datetime.timedelta(days = 1) - datetime.timedelta(hours = 8)).isoformat() + 'Z',
            "destinations"  : [],
            "dependencies"  : [],
            "properties"    : []
        }

    def getOrder(self):
        '''
        get order data (type: dict)
        '''
        return self._order

    @utils.mb_default_catch_exception
    @accepts.mb_accepts(str)
    def setIntendedVehicle(self, vehicle = "undefine_vehicle"):
        '''
        intended vehicle is optional
        '''
        self._order["intendedVehicle"] = vehicle


    @utils.mb_default_catch_exception
    @accepts.mb_accepts(datetime.datetime)
    def setDeadline(self, deadline = None):
        '''
        concrete a ISO8601 time with 'Z' !!!
        deadline is required !!!
        '''
        if deadline is None:
            deadline = datetime.datetime.now()
        self._order["deadline"] = (deadline - datetime.timedelta(hours = 8)).isoformat() + 'Z'


    @utils.mb_default_catch_exception
    @accepts.mb_accepts(str)
    def setCategory(self, category = "-"):
        '''
        order category is optional
        '''
        self._order["category"] = category


    @utils.mb_default_catch_exception
    @accepts.mb_accepts(str, str)    
    def addDestination(self, location = 'undefine_location', operation = 'undefine_operation', *properties):
        '''
        there is at least one destination
        '''
        desti = {"locationName" : location, "operation" : operation, "properties" : []}
        if True == TransportOrder._checkProperties(properties):
            desti['properties'] = properties
        else:
            self._log.info("wrong destination properties with " + str(properties))
        
        self._order.get("destinations").append(desti)


    @utils.mb_default_catch_exception
    def addOrderProperties(self, *properties):
        '''
        add transport order properties. this is optional
        '''
        if True == TransportOrder._checkProperties(properties):
            self._order.get("properties").extend(properties)
        else:
            self._log.info("wrong order properties with " + str(properties))

    @utils.mb_default_catch_exception
    def addOrderDependencies(self, *dependencies):
        '''
        add transport order dependencies. this is optional
        '''
        self._order.get("dependencies").extend(dependencies)


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
        return json.dumps(self._order)




if __name__ == '__main__':
    t = TransportOrder()
    print(TransportOrder)
    m = {}
    li = ({
    "key" : "transport order-specific key",
    "value" : "some value"
    },{
        "key" : "sssssssssss key",
        "value" : "some value"
    })
    t.addDestination("aaa","bbb",*li)
    print(t.encode())
    