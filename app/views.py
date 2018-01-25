import time
from flask import Flask
from flask_mako import MakoTemplates
from flask_mako import render_template
from libs.NBAGames import NBAGames


app = Flask(__name__)
mako = MakoTemplates(app)
title_prefix = "A personal blog belongs to PerseusH"


@app.route("/")
def index():
    return _render("index.html")


@app.route("/hello/")
@app.route("/hello/<path:username>", methods=["GET", "POST"])
def hello(username=""):
    banner = 'Hello%s%s!' % (username and ' ', username)
    return _render("hello.html", banner, banner=banner)


@app.route("/nba/")
def nba():
    today = time.strftime("%Y-%m-%d", time.localtime())
    return _render("nba.html", 'NBAGames', **{'games': NBAGames(), 'today': today})


def _render(f, title=None, **kv):
    if title:
        kv['title'] = '%s - %s' % (title_prefix, title)
    else:
        kv['title'] = title_prefix

    return render_template(f, **kv)


if __name__ == "__main__":
    mako.debug = True
    mako.run(host="0.0.0.0")
