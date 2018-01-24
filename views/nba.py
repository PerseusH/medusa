import time
from flask import Flask, render_template
from libs.NBAGames import NBAGames


app = Flask(__name__)


@app.route("/nba/")
def nba():
    today = time.strftime("%Y-%m-%d", time.localtime())
    return render_template("nba.html", **{'games': NBAGames(), 'today': today})

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
