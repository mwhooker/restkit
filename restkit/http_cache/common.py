from collections import MutableMapping


class StorageInterface(MutableMapping):
    """Interface to the cache stores

    A subset of collections.MutableMapping"""

    def __delitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


class BoundedDict(dict):
    """Dictionary of bounded size.

    When a put is made that would cause the BoundedDict to go over its
    size limit, it first removes an arbitrary value to make room. If
    more well-defined behavior is desired, use restkit.ext.lru_cache."""

    def __init__(self, max_size=1024):
        if max_size < 1:
            raise ValueError(
                "max_size must be a positive integer greater than 0")
        self.max_size = max_size

    def __setitem__(self, key, value):
        if len(self) >= self.max_size:
            self.popitem()

        dict.__setitem__(self, key, value)
