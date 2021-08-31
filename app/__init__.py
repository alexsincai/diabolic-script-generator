from flask import Flask, render_template, request, jsonify
from .diabolic import Diabolic


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    text = (
        request.json.get("text")
        if request.is_json
        else request.values.get("text")
        if request.method in ["GET", "POST"]
        else None
    )
    url = Diabolic(text).data_url if text is not None else None
    error = None

    if request.is_json:
        return jsonify({"url": url,})

    return render_template(
        "index.html",
        url=url,
        text=text,
        error=error,
    )


@app.route("/about")
def about():
    return render_template("about.html")
