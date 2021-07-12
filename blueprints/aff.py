#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# (c)2021 .direwolf <kururinmiracle@outlook.com>
# Licensed under the MIT License.

from flask import Blueprint, request
from arcfutil import aff as a
from arcfutil import exception as aex

bp = Blueprint('aff', __name__, url_prefix='/aff')


@bp.route('/')
def affroot():
    return 'Hi, here is aff api!'


@bp.route('/parser/loadline', methods=['GET'])
def parser_loadline():
    notestring = request.args.get('note')

    try:
        if notestring is not None:
            single_note = a.load(notestring)[0]
        else:
            return {
                'status': 'fail',
                'result': '传入值为空或者无效'
            }
    except aex.AffNoteValueError as e:
        return {
            'status': 'fail',
            'result': 'Note数值非法: ' + str(e)
        }
    except Exception as e:
        return {
            'status': 'fail',
            'result': '未知错误: ' + str(e)
        }

    result = single_note.__dict__
    result['status'] = 'success'
    return result


@bp.route('/arc/split', methods=['GET'])
def arc_split():
    arcstring = request.args.get('arcstring')
    arcobj = a.load(arcstring)[0]
    if not isinstance(arcobj, a.Arc):
        return {
            'status': 'fail',
            'result': '传入值不是Arc的表达式: ' + arcstring
        }

    paradict = request.args.to_dict()
    if 'start' in paradict:
        start = int(paradict['start'])
    else:
        start = arcobj.time
    if 'stop' in paradict:
        stop = int(paradict['stop'])
    else:
        stop = arcobj.totime
    if 'count' in paradict:
        step = int((stop - start) / int(paradict['count']))
        if int(paradict['count']) > 512:
            return {
                'status': 'fail',
                'result': '细分数量过大（最大支持512细分）'
            }
        if step < 1:
            step = 1
    else:
        step = None

    return {
        'status': 'success',
        'result': str(a.NoteGroup(arcobj[start:stop:step]))
    }


@bp.route('/arc/crease-line', methods=['GET'])
def arc_crease_line():
    arcstring = request.args.get('arcstring')
    x_range = request.args.get('x_range')
    y_range = request.args.get('y_range')
    count = request.args.get('count')
    mode = request.args.get('mode')
    if mode is None:
        mode = 'm'
    if int(count) > 512:
        return {
            'status': 'fail',
            'result': '细分数量过大（最大支持512细分）'
        }

    arcobj = a.loadline(arcstring)
    if not isinstance(arcobj, a.Arc):
        return {
            'status': 'fail',
            'result': '传入值不是Arc的表达式: ' + arcstring
        }

    try:
        arclist = a.generator.arc_crease_line(arcobj, float(x_range), float(y_range), int(count), mode=mode)
    except Exception as e:
        return {
            'status': 'fail',
            'result': str(e)
        }

    return {
        'status': 'success',
        'result': str(arclist)
    }


@bp.route('/arc/rain', methods=['GET'])
def arc_rain():
    start = request.args.get('start')
    stop = request.args.get('stop')
    step = request.args.get('step')
    length = request.args.get('length')

    count = (int(stop) - int(start)) / int(step)
    if count > 512:
        return {
            'status': 'fail',
            'result': '细分数量过大（最大支持512细分）'
        }

    try:
        arclist = a.generator.arc_rain(int(start), int(stop), int(step), int(length) if length is not None else None)
    except Exception as e:
        return {
            'status': 'fail',
            'result': str(e)
        }

    return {
        'status': 'success',
        'result': str(arclist)
    }


@bp.route('/timing/easing', methods=['GET'])
def timing_easing():
    start = request.args.get('start')
    stop = request.args.get('stop')
    start_bpm = request.args.get('start_bpm')
    stop_bpm = request.args.get('stop_bpm')
    count = request.args.get('count')
    bar = request.args.get('bar')

    if int(count) > 512:
        return {
            'status': 'fail',
            'result': '细分数量过大（最大支持512细分）'
        }

    try:
        arclist = a.generator.timing_easing_linear(
            int(start), int(stop), float(start_bpm), float(stop_bpm), int(count),
            float(bar) if bar is not None else 4.00
        )
    except Exception as e:
        return {
            'status': 'fail',
            'result': str(e)
        }

    return {
        'status': 'success',
        'result': str(arclist)
    }


@bp.route('/timing/glitch', methods=['GET'])
def timing_glitch():
    start = request.args.get('start')
    stop = request.args.get('stop')
    count = request.args.get('count')
    bpm_range = request.args.get('bpm_range')
    exact_bar = request.args.get('bar_base')
    zero_bar = request.args.get('bar_zero')

    if int(count) > 512:
        return {
            'status': 'fail',
            'result': '细分数量过大（最大支持512细分）'
        }

    try:
        arclist = a.generator.timing_glitch(
            int(start), int(stop), int(count), float(bpm_range),
            float(exact_bar) if exact_bar is not None else 4.00,
            float(zero_bar) if zero_bar is not None else 4.00
        )
    except Exception as e:
        return {
            'status': 'success',
            'result': str(e)
        }

    return {
        'status': 'success',
        'result': str(arclist)
    }
