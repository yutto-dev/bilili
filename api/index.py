import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.insert(0, BASE_DIR)

from functools import wraps

import bilili.api.acg_video
import bilili.api.bangumi
import bilili.api.danmaku
import bilili.api.subtitle
from bilili.api.exports import exports
from bilili.api.exceptions import APIException
from flask import Flask, Response, jsonify, make_response, request

app = Flask(__name__)
name_index = 0


def add_params(func):
    @wraps(func)
    def func_wrapper():
        params = dict(request.args)
        response = func(**params)
        return jsonify(response)

    return func_wrapper


def unique_name(func):
    global name_index
    name_index += 1

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    func_wrapper.__name__ = "{}_{:03d}".format(func.__name__, name_index)
    return func_wrapper


def export_api(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            # fmt: off
            return {
                "code": 0,
                "message": "",
                "data": func(*args, **kwargs),
            }
        except APIException as e:
            # fmt: off
            return {
                "code": e.code,
                "message": e.message,
                "data": {},
            }
        except Exception as e:
            # fmt: off
            return {
                "code": 200,
                "message": e.args[0],
                "data": {},
            }
    return func_wrapper


for route, export_func in exports.items():
    @app.route("/api/v0" + route, methods=["GET"])
    @add_params
    @unique_name
    @export_api
    def func(export_func=export_func, *args, **kwargs):
        return export_func(*args, **kwargs)


if __name__ == "__main__":
    app.run(debug=True)
