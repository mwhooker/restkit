# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license.
# See the NOTICE for more information.


import logging
import collections
from hashlib import md5
from urlparse import urlsplit
from restkit.http_cache.common import BoundedDict


log = logging.getLogger(__name__)


class HttpCache(object):
    """filter for http caching. Caches GET requests using supplied engine

    on response the filter stores the result in the storage engine, which by
    default is an in-memory LRU cache.

    on the next request for that resource, the filter will inject
    'if-none-match' and 'if-modified-since' headers (if they exist) into the
    request headers. If a 304 status is returned on response, the filter will
    return the cached result.

    TODO:
          * follow cachability guidelines:
            - http://tools.ietf.org/html/rfc2616#section-13 (general)
            - http://tools.ietf.org/html/rfc2616#section-13.4 (specific)
              * check the `Expires` header to see if we should even make a request
                - http://tools.ietf.org/html/rfc2616#section-13.2
          * consider carefully which headers to store (expires, etag,
              last-modified, url, etc.)
          * have the option to send HEAD request in lieu of GET if we have
              cache headers around (http://tools.ietf.org/html/rfc2616#section-9.4)
          * break http cache into more general cache interface for the filter to
              use

    """

    def __init__(self, cache=BoundedDict()):
        if not isinstance(cache, collections.MutableMapping):
            raise TypeError
        self.cache_engine = cache

    def _generate_cache_key(self, req):
        #strip out username and password
        url = ''.join(urlsplit(req.final_url)[1:4])
        return "%s:%s" % (req.method, url)

    def _request_cachable(self, req):
        #only cache GET requests
        if req.method != "GET":
            return True

    def on_request(self, req):
        """ Set up http caching headers
            1. search for request in cache
            2. inject if-none-match and If-Modified-Since headers
        """

        if not self._request_cachable(req):
            return

        key = self._generate_cache_key(req)
        log.debug("caching key %s" % key)

        if key in self.cache_engine:
            cache_obj = self.cache_engine[key]

            log.debug("injecting caching headers %s" % cache_obj['headers'])
            if 'etag' in cache_obj['headers']:
                req.headers.append(('If-None-Match',
                                    cache_obj['headers']['etag']))
            if 'last-modified' in cache_obj['headers']:
                req.headers.append(('If-Modified-Since',
                                    cache_obj['headers']['last-modified']))

    def on_response(self, req):
        """retrieve response from cache if not modified
            1. if status is 304
                - search cache for and return response obj
            2. if status is 200
                - add to cache
        """

        if not self._request_cachable(req):
            return

        url_key = self._generate_cache_key(req)

        if req.parser.status_int == 200:
            headers = {}
            for key, value in req.parser.headers:
                headers[key.lower()] = value.rstrip()

            cache_obj = {'headers': headers, 'body': req.response_body}
            self.cache_engine[url_key] = cache_obj
        elif req.parser.status_int == 304:
            log.info('304 response found. returning cached body')
            cache_obj = self.cache_engine[url_key]
            req.response_body = cache_obj['body']
