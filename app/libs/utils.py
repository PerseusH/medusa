# -*- coding:utf-8 -*-


import os
import time
import logging


def get_last_modified(filename):
    """
    Get last modified time of a named file.
    """

    _modified_time = os.path.getmtime(filename)
    _modified_time = time.strptime(time.ctime(_modified_time), "%a %b %d %H:%M:%S %Y")
    _modified_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", _modified_time)

    return _modified_time


def make_response(data, cached=False, **headers):
    """
    Make response for a web request.
    """

    from flask import request, make_response

    if_modified_since = request.environ.get("HTTP_IF_MODIFIED_SINCE", None)
    if_none_match = request.environ.get("HTTP_IF_NONE_MATCH", None)

    if cached and (if_modified_since or if_none_match) and not \
            (if_modified_since and if_modified_since != headers["Last-Modified"] or \
            if_none_match and if_none_match != headers["Etag"]):
            response = make_response("", 304)
    else:
        response = make_response(data)
        response.headers = headers

    return response


def _json():
    """
    Get the fastest json parser.
    """
    import simplejson
    if bool(getattr(simplejson, '_speedups', False)):
        json = simplejson
        logging.info('Using simplejson.')
    else:
        import json
        logging.info('Using json.')

    return json

json = _json()
