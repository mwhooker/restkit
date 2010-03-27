# -*- coding: utf-8 -
#
# This file is part of restkit released under the MIT license. 
# See the NOTICE for more information.


import logging
from restkit.http_cache import LRUCache
from restkit import tee
from hashlib import md5

log = logging.getLogger(__name__)


class HttpCache(object):
    ETAG_HEADER = 'If-None-Match'
    MODIFIED_HEADER = 'If-Modified-Since'

    def __init__(self, cache=LRUCache()):
        self.cache_engine = cache

    def _make_key(self, req):
        return md5(str(req.method) + str(req.final_url)).hexdigest()

    def on_request(self, req):
        """ Set up http caching headers
            1. search for request in cache
            2. inject if-none-match and If-Modified-Since headers
        """
        key = self._make_key(req)
        log.debug("generating hash for request: %s" % key)
        if key in self.cache_engine:
            cache_obj = self.cache_engine[key]

            log.debug("retrieved headers: %s" % cache_obj['headers'])
            if 'etag' in cache_obj['headers']:
                req.headers.append(('If-None-Match', cache_obj['headers']['etag']))
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
        url_key = self._make_key(req)

        if req.parser.status_int == 200:
            headers = {}
            for key, value in req.parser.headers:
                headers[key.lower()] = value
                
            cache_obj = {'headers': headers, 'body': req.response_body}
            self.cache_engine[url_key] = cache_obj
        elif req.parser.status_int == 304:
            cache_obj = self.cache_engine[url_key]
            req.response_body = cache_obj['body']




        """
        # from
        # http://code.google.com/p/feedparser/source/browse/trunk/feedparser/feedparser.py

        if etag:
            request.add_header('If-None-Match', etag)
        if type(modified) == type(''):
            modified = _parse_date(modified)
        if modified:
            # format into an RFC 1123-compliant timestamp. We can't use
            # time.strftime() since the %a and %b directives can be affected
            # by the current locale, but RFC 2616 states that dates must be
            # in English.
            short_weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            request.add_header('If-Modified-Since', '%s, %02d %s %04d %02d:%02d:%02d GMT' % (short_weekdays[modified[6]], modified[2], months[modified[1] - 1], modified[0], modified[3], modified[4], modified[5]))    
        """

