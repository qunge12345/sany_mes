import sys
import utils
import redis
import json
import time
import datetime

class MessageTest(object):

    def __init__(self, loggerName = 'test'):
        self.log = utils.logger().getLogger('test')

    def listenHandler(self):
        '''
        listen from redis
        '''
        # establish redis
        r = redis.StrictRedis(host = 'localHost', port = 6379, db = 0)
        p = r.pubsub()
        p.psubscribe("*")

        #listening
        for item in p.listen():
            self.log.info(item)

if __name__ == '__main__':
    m = MessageTest()
    m.listenHandler()
