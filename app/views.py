import os
import time
from hashlib import sha1
from flask import Flask
from flask import request
from flask_mako import MakoTemplates
from flask_mako import render_template
from libs.NBAGames import NBAGames
from libs.utils import get_last_modified
from libs.utils import make_response
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
        _last_modified = get_last_modified("templates/index.html")
        _cache["index"] = _index_cache = (_etag, _last_modified)
    etag, last_modified = _index_cache

    print request.environ

    return make_response(
            data_page,
            cached=True,
            **{
                "Content-Type": "text/html; charset=utf-8",
                "Etag": etag,
                "Last-Modified": last_modified
                }
            )


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

    today = time.strftime("%Y-%m-%d", time.localtime())

    data_page = _render("nba.html", "NBAGames", **{"games": games, "today": today})

    return make_response(
            data_page,
            cached=True,
            **{
                "Content-Type": "text/html; charset=utf-8",
                "Etag": etag
                }
            )


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


def _render(templ, title=None, **kv):
    kv["title"] = "%s - %s" % (title_prefix, title) if title else title_prefix

    return render_template(templ, **kv)


if __name__ == "__main__":
    mako.debug = True
    mako.run(host="0.0.0.0")
