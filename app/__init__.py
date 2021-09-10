"""The generator server"""

from flask import Flask, render_template, request, jsonify
from .diabolic import Diabolic


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """The main function

    Returns:
        str: HTML or JSON for given text
    """
    text = (
        request.json.get("text")
        if request.is_json
        else request.values.get("text")
        if request.method in ["GET", "POST"]
        else None
    )
    url = Diabolic(text).data_url if text is not None else None

    if request.is_json:
        return jsonify({"url": url})

    return render_template(
        "index.html",
        url=url,
        text=text,
    )


@app.route("/about")
def about() -> str:
    """About page

    Returns:
        str: HTML
    """
    return render_template("index.html", about=True)
