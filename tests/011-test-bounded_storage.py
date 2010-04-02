# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license.
# See the NOTICE for more information.

import t
import unittest

from restkit.http_cache import BoundedDict
try:
    from restkit.ext.lru_cache import LRUCache
    lru_loaded = True
except ImportError:
    lru_loaded = False


class BoundedStructure(object):
    CacheEngine = None

    def test_001(self):
        """test set/store"""
        cache = self.CacheEngine()
        key = "lru_key"
        value = "lru_value"

        cache[key] = value

        t.eq(cache[key], value)

    def test_002(self):
        """test key eviction"""
        cache = self.CacheEngine(1)
        key = "lru_key"
        value = "lru_value"

        cache[key] = value
        cache['trash'] = 'junk'

        t.ne(cache.get(key), value)


class TestBoundedDict(unittest.TestCase, BoundedStructure):
    CacheEngine = BoundedDict

if lru_loaded:

    class TestLRUCache(unittest.TestCase, BoundedStructure):
        CacheEngine = LRUCache
