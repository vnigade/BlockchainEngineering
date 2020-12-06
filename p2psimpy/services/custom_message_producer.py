# Message gossip
from p2psimpy import *
from p2psimpy.services.base import BaseRunner
from p2psimpy.messages import BaseMessage
from p2psimpy.storage.simple import Storage
from p2psimpy.services.custom_gossip import GossipMessage

from re import split 
from copy import copy

class MessageProducer(BaseRunner):

    def __init__(self, peer, init_timeout=1000, msg_rate=5, init_ttl=3, init_fanout=10, msg_count=20):
        '''
        init_timeout: milliseconds to wait before starting the message production. 
        msg_rate: number of messages per second
        init_ttl: ttl to set up for the message 
        init_fanout: to how many peer send the message to
        '''
        super().__init__(peer)

        # calculate tx_interval
        self.init_timeout = init_timeout
        self.init_ttl = init_ttl
        self.init_fanout = init_fanout
        
        self.tx_interval = 1000 / msg_rate
        self.counter = 1
        
        # Note that we are going to limit the number of messages. Because, depending on the network
        # topology, messages might take longer time to converge. And therefore when simulation ends, last few messages in the
        # run might not have been converged, which leads to NaN values.
        self.msg_count = 20
        
        # Let's add a storage layer to store messages
        self.strg_name = 'msg_time'
        self.peer.add_storage(self.strg_name, Storage())


    def produce_transaction(self):
        # Create a gossip message: message counter, peer_id and gossip it   
        self.peer.gossip(GossipMessage(self.peer,
                                       '_'.join((str(self.counter), str(self.peer.peer_id))), 
                                       self.init_ttl), 
                         self.init_fanout)
        # Locally store the message counter 
        self.peer.store(self.strg_name, str(self.counter), self.peer.env.now)
        self.counter+=1
        

    def run(self):
        # Wait the initial timeout
        yield self.env.timeout(self.init_timeout)
        # while True:
        while self.counter <= self.msg_count:
            self.produce_transaction()
            yield self.env.timeout(self.tx_interval)