#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# (c)2021 .direwolf <kururinmiracle@outlook.com>
# Licensed under the MIT License.

from flask import Flask
from dotenv import load_dotenv
from . import common_responses

load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    from .blueprints import aff
    app.register_blueprint(aff.bp)

    @app.route('/')
    def root():
        return 'Welcome to .direwolf\'s api :)'

    return app
