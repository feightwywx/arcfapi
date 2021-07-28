#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# (c)2021 .direwolf <kururinmiracle@outlook.com>
# Licensed under the MIT License.

from flask import Response, make_response

def make_success_response(result: str) -> Response:
    return make_response({
        'status': 'success',
        'result': result
    }, 200, {'Access-Control-Allow-Origin': '*'})

def make_fail_response(result: str) -> Response:
    return make_response({
        'status': 'fail',
        'result': result
    }, 200, {'Access-Control-Allow-Origin': '*'})

