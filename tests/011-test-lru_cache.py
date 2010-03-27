# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license. 
# See the NOTICE for more information.

import t

from restkit.http_cache import LRUCache

def test_001():
    """test set/store"""
    cache = LRUCache()
    key = "lru_key"
    value = "lru_value"

    cache[key] = value

    t.eq(cache[key], value)


def test_001():
    """test key eviction"""
    cache = LRUCache(1)
    key = "lru_key"
    value = "lru_value"

    cache[key] = value
    cache['trash'] = 'junk'

    t.ne(cache.get(key), value)
