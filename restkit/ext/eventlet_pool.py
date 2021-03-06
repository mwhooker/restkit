# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license. 
# See the NOTICE for more information.

import collections
import eventlet
from eventlet import queue

from restkit.pool import PoolInterface
from restkit import sock

class _Host(object):
    
    def __init__(self, address):
        self._addr = address
        self.pool = queue.LightQueue(0)
        self.free_connections = collections.deque()
        self.nb_connections = 0
        
    def waiting(self):
        return max(0, self.pool.getting() - self.pool.putting())    
    
class EventletPool(PoolInterface):
    """
    Eventlet pool to manage connections. after a specific timeout the
    sockets are closes. Default timeout is 300s.
    
    To use restkit with eventlet::
    
        import eventlet
        eventlet.monkey_patch(all=False, socket=True)
        from restkit import request
        from restkit.ext.eventlet_pool import EventletPool
        pool = EventletPool(max_connections=5)
        r = request('http://friendpaste.com', pool_instance=pool)
        
    """
    
    def __init__(self, max_connections=4, timeout=300):
        """ Initialize EventletPool 
        
        :param max_connexions: int, number max of connections in the pool. 
        Default is 4
        :param timeout: int, number max of second a connection is kept alive. 
        Default is 300s.
        """
        self.max_connections = max_connections
        self.timeout = 60
        self.hosts = {}
        self.sockets = {}
                
    def get(self, address):
        """ Get connection for (Host, Port) address 
        :param address: tuple (Host, address)
        """
        
        host = self.hosts.get(address)
        if not host:
            return None
        if host.free_connections:
            socket = host.free_connections.popleft()
            eventlet.spawn(self._remove_socket, socket)
            return socket
        if host.nb_connections < self.max_connections:
            host.nb_connections += 1
            return None
        socket = host.pool.get()
        eventlet.spawn(self._remove_socket, socket)
        return socket
                
    def _monitor_socket(self, fn):
        """ function used to monitor the socket """
        if fn in self.sockets:
            socket = self.sockets[fn]
            sock.close(socket)
            del self.sockets[fn]
                
    def monitor_socket(self, socket):
         self.sockets[socket.fileno()] = socket
         eventlet.spawn_after(self.timeout, self._monitor_socket, socket.fileno())
        
    def put(self, address, socket):
        """ release socket in the pool 
        
        :param address: tuple (Host, address)
        :param socket: a socket object 
        """
        host = self.hosts.get(address)
        if not host:
            host = _Host(address)
            
        if host.nb_connections > self.max_connections:
            sock.close(socket)
            host.nb_connections -= 1
        
        elif host.waiting():
            host.pool.put(socket)
            self.monitor_socket(socket)
        else:
            host.free_connections.append(socket)
            self.monitor_socket(socket)
     
        
    def clean(self, address):
        """ close all sockets in the pool for this address 
        
        :param address: tuple (Host, address)
        """
        host = self.hosts.get(address)
        if not host:
            return
        if host.free_connections:
            while host.free_connections:
                socket = host.free_connections.popleft()
                sock.close(socket)
            while host.nb_connections:
                socket = host.pool.get()
                sock.close(socket)
                host.nb_connections -= 1
