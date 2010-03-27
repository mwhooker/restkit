# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license. 
# See the NOTICE for more information.

import t
from restkit import request
from restkit.http_cache import HttpCache

from _server_test import HOST, PORT


@t.client_request("/cache", filters=[HttpCache()])
def test_001(u, c):
    
    r = c.request(u)
    t.eq(r.status_int, 200)
    t.eq(r.body, "ok")

    r = c.request(u)
    t.eq(r.status_int, 304)
    t.eq(r.body, "ok")
