from restkit.http_cache import StorageInterface
from repoze.lru import LRUCache as LRUCacheEngine


class LRUCache(StorageInterface):
    """In memory LRU cache"""

    def __init__(self, max_size=1024):
        if max_size < 1:
            raise ValueError(
                "max_size must be a positive integer greater than 0")
        self.max_size = max_size
        self.engine = LRUCacheEngine(max_size)

    def __getitem__(self, key):
        value = self.engine.get(key)
        if value is None:
            raise KeyError
        return value

    def __setitem__(self, key, value):
        self.engine.put(key, value)

    def __contains__(self, key):
        value = self.engine.get(key)
        if value is not None:
            return True
        else:
            return False

    def __len__(self):
        return self.max_size
