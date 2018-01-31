import os
import time
from hashlib import sha1
from flask import Flask
from flask import request
from flask import make_response
from flask_mako import MakoTemplates
from flask_mako import render_template
from libs.NBAGames import NBAGames
from datamap import datamap


app = Flask(__name__)
mako = MakoTemplates(app)
title_prefix = "A personal blog belongs to PerseusH"
_cache = dict()

@app.route("/")
def index():
    data_page = _render("index.html")

    print type(request.headers)
    print request.headers

    global _cache
    _index_cache = _cache.get("index")
    if not _index_cache:
        _etag = sha1(repr(data_page)).hexdigest()
        _modified_time = os.path.getmtime("templates/index.html")
        _modified_time = time.strptime(time.ctime(_modified_time), "%a %b %d %H:%M:%S %Y")
        _modified_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", _modified_time)
        _cache["index"] = _index_cache = (_etag, _modified_time)
    etag, modified_time = _index_cache

    print request.environ
    #if request.environ.get("HTTP_IF_NONE_MATCH", None) == etag:
    if request.environ.get("HTTP_IF_MODIFIED_SINCE", None) == modified_time:
        response = make_response("", 304)
    else:
        response = make_response(data_page)
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        response.headers["Etag"] = etag
        response.headers["Last-Modified"] = modified_time
    
    return response


@app.route("/hello/")
@app.route("/hello/<path:username>", methods=["GET", "POST"])
def hello(username=""):
    banner = "Hello%s%s!" % (username and " ", username)
    return _render("hello.html", banner, banner=banner)


@app.route("/nba/")
def nba():
    global _cache
    _nba_cache = _cache.get("nba")
    if not _nba_cache:
        _games = NBAGames()
        _etag = sha1(repr(_games)).hexdigest()
        _cache["nba"] = _nba_cache = (_games, _etag)
    games, etag = _nba_cache

    if request.environ.get("HTTP_IF_NONE_MATCH", None) == etag:
        response = make_response("", 304)
    else:
        today = time.strftime("%Y-%m-%d", time.localtime())
        response = make_response(_render("nba.html", "NBAGames", **{"games": games, "today": today}))
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        response.headers["Etag"] = etag

    return response


@app.route("/python/")
@app.route("/python/<path:filename>", methods=["GET"])
def python(filename=""):
    if not filename:
        filelist = os.listdir("templates/data/python")
        filelist = {f[:f.rfind(".")]: datamap["Python"][f[:f.rfind(".")]] for f in filelist}
        
        return _render("python.html", filelist=filelist)
    else: 
        filename = filename[:filename.rfind(".")]
        return _render("python.html", **{"filename": filename, "filetitle": datamap["Python"][filename]})


def _render(f, title=None, **kv):
    if title:
        kv["title"] = "%s - %s" % (title_prefix, title)
    else:
        kv["title"] = title_prefix

    return render_template(f, **kv)


if __name__ == "__main__":
    mako.debug = True
    mako.run(host="0.0.0.0")
