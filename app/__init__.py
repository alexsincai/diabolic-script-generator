from flask import Flask

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    pass


@app.route("/about")
def about():
    pass
