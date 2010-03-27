from restkit.http_cache.lru_cache import LRUCache
from restkit.http_cache.http_cache import HttpCache

class HttpCacheInterface(object):
    """ abstract class from which 
    all cache engines should inherit
    """

    def get(self, key):
        """ method used to return a request from the cache"""
        raise NotImplementedError
        
    def put(self, key, req):
        """ Put a request into the cache"""
        raise NotImplementedError
        
    def clear(self):
        """ method used to clear the cache """
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError
        
    def __iter__(self):
        raise NotImplementedError
