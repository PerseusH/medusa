import time
from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def index():
    return "Welcome to Flask!"


@app.route("/hello/")
@app.route("/hello/<path:username>", methods=["GET", "POST"])
def hello(username=""):
    return render_template("hello.html", username=username)


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")
