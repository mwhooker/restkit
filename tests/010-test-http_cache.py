# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license. 
# See the NOTICE for more information.

import t
import collections
from restkit import request
from restkit.http_cache import HttpCache

from _server_test import HOST, PORT

class NoCache(dict):
    def __getitem__(self, key):
        assert False

    def __setitem__(self, key, value):
        assert False

@t.client_request("/cache", filters=[HttpCache()])
def test_001(u, c):
    
    r = c.request(u)
    t.eq(r.status_int, 200)
    t.eq(r.body, "ok")

    r = c.request(u)
    t.eq(r.status_int, 304)
    t.eq(r.body, "ok")


@t.client_request("/cache", filters=[HttpCache(cache=NoCache())])
def test_002(u, c):
    """test that it doesn't cache POSTS"""
    
    r = c.request(u, method='PUT')
    t.eq(r.status_int, 200)
    t.eq(r.body, "ok")

