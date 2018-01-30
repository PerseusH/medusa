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
_index_cache = dict()

@app.route("/")
def index():
    data = _render("index.html")
    global _index_cache
    print type(request.headers)
    print request.headers

    if not _index_cache.get("templ"):
        _index_cache["templ"] = sha1(repr(data)).hexdigest()
    datahash = _index_cache["templ"]

    if not _index_cache.get("modifiedtime"):
        modified_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        _index_cache["modifiedtime"] = modified_time
    modified_time = _index_cache["modifiedtime"]

    print request.environ
    #if request.environ.get("HTTP_IF_NONE_MATCH", None) == datahash:
    if request.environ.get("HTTP_IF_MODIFIED_SINCE", None) == modified_time:
        response = make_response("", 304)
    else:
        response = make_response(data)
        response.headers["Content-Type"] = "text/html; charset=utf-8"
        response.headers["Etag"] = datahash
        response.headers["Last-Modified"] = modified_time
    
    return response


@app.route("/hello/")
@app.route("/hello/<path:username>", methods=["GET", "POST"])
def hello(username=""):
    banner = "Hello%s%s!" % (username and " ", username)
    return _render("hello.html", banner, banner=banner)


@app.route("/nba/")
def nba():
    print request.headers
    today = time.strftime("%Y-%m-%d", time.localtime())
    return _render("nba.html", "NBAGames", **{"games": NBAGames(), "today": today})


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
