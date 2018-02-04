import os
import time
import datamap
import config
from hashlib import sha1
from flask import Flask
from flask import request
from flask_mako import MakoTemplates
from flask_mako import render_template
from libs.NBAGames import NBAGames
from libs.utils import get_last_modified
from libs.utils import make_response


app = Flask(
        __name__,
        template_folder=config.dir_templ,
        static_folder=config.dir_static
        )
mako = MakoTemplates(app)
_dirdata = config.dir_data
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
    _dirpath = _dirdata + "/python"
    _map = datamap.Python

    if not filename:
        filelist = os.listdir(_dirpath)
        filelist = {f[:f.rfind(".")]: _map[f[:f.rfind(".")]] for f in filelist}
        
        return _render("python.html", filelist=filelist)
    else: 
        filename = filename[:filename.rfind(".")]

        return _render("python.html", **{
            "filename": filename + ".txt",
            "dirpath": _dirpath,
            "filetitle": _map[filename]
            }
            )


def _render(templ, title=None, **kv):
    kv["title"] = "%s - %s" % (config.title_prefix, title) if title else config.title_prefix

    return render_template(templ, **kv)


if __name__ == "__main__":
    mako.debug = True
    mako.run(host="0.0.0.0")
