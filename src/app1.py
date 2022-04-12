import sys

from flask import Flask, render_template, request
from typing import List, Dict
from handler_db import HandlerDb
from handler_user_db import HandlerUserDb
from model.user import User

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello, World"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
