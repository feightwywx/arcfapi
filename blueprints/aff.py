#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# (c)2021 .direwolf <kururinmiracle@outlook.com>
# Licensed under the MIT License.

from arcfutil.aff.note import arc
from flask import Blueprint, request
from arcfutil import aff as a
from arcfutil import exception as aex
from ..common_responses import make_success_response, make_fail_response

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
            return make_fail_response('传入值为空或者无效')
    except aex.AffNoteValueError as e:
        return make_fail_response('Note数值非法: ' + str(e))
    except Exception as e:
        return make_fail_response('未知错误: ' + str(e))

    result = single_note.__dict__
    return make_success_response(result)


@bp.route('/arc/split', methods=['GET'])
def arc_split():
    arcstring = request.args.get('arcstring')
    arcobj = a.load(arcstring)[0]
    if not isinstance(arcobj, a.Arc):
        return make_fail_response('传入值不是Arc的表达式: ' + arcstring)

    paradict = request.args.to_dict()
    if 'start' in paradict:
        start = int(paradict['start'])
        if start > arcobj.totime:
            return make_fail_response('起始时间点大于结束时间点')
    else:
        start = None
    if 'stop' in paradict:
        stop = int(paradict['stop'])
        if stop < arcobj.time:
            return make_fail_response('结束时间点小于起始时间点')
    else:
        stop = None
    if 'count' in paradict:
        count = int(paradict['count'])
        if count > 512:
            return make_fail_response('细分数量过大（最大支持512细分）')

    return make_success_response(str(a.generator.arc_slice_by_count(
        arc=arcobj,
        count=count,
        start=start,
        stop=stop
    )))


@bp.route('/arc/crease-line', methods=['GET'])
def arc_crease_line():
    arcstring = request.args.get('arcstring')
    x_range = request.args.get('x_range')
    y_range = request.args.get('y_range')
    count = request.args.get('count')
    mode = request.args.get('mode')
    easing = request.args.get('easing')
    if mode is None:
        mode = 'm'
    if int(count) > 512:
        return make_fail_response('细分数量过大（最大支持512细分）')
    
    if easing is None:
        easing = 's'

    arcobj = a.loadline(arcstring)
    if not isinstance(arcobj, a.Arc):
        return make_fail_response('传入值不是Arc的表达式: ' + arcstring)

    try:
        arclist = a.generator.arc_crease_line(arcobj, float(x_range), float(y_range), int(count), mode=mode, easing=easing)
    except Exception as e:
        return make_fail_response('未知错误: ' + str(e))

    return make_success_response(str(arclist))


@bp.route('/arc/rain', methods=['GET'])
def arc_rain():
    start = request.args.get('start')
    stop = request.args.get('stop')
    step = request.args.get('step')
    length = request.args.get('length')

    count = (int(stop) - int(start)) / int(step)
    if count > 512:
        return make_fail_response('细分数量过大（最大支持512细分）')

    try:
        arclist = a.generator.arc_rain(int(start), int(stop), int(step), int(length) if length is not None else None)
    except Exception as e:
        return make_fail_response('未知错误: ' + str(e))

    return make_success_response(str(arclist))


@bp.route('/timing/easing', methods=['GET'])
def timing_easing():
    start = request.args.get('start')
    stop = request.args.get('stop')
    start_bpm = request.args.get('start_bpm')
    stop_bpm = request.args.get('stop_bpm')
    count = request.args.get('count')
    bar = request.args.get('bar')

    if int(count) > 512:
        return make_fail_response('细分数量过大（最大支持512细分）')

    try:
        arclist = a.generator.timing_easing_linear(
            int(start), int(stop), float(start_bpm), float(stop_bpm), int(count),
            float(bar) if bar is not None else 4.00
        )
    except Exception as e:
        return make_fail_response('未知错误: ' + str(e))

    return make_success_response(str(arclist))


@bp.route('/timing/glitch', methods=['GET'])
def timing_glitch():
    start = request.args.get('start')
    stop = request.args.get('stop')
    count = request.args.get('count')
    bpm_range = request.args.get('bpm_range')
    exact_bar = request.args.get('exact_bar')
    zero_bar = request.args.get('zero_bar')

    if int(count) > 512:
        return make_fail_response('细分数量过大（最大支持512细分）')

    try:
        arclist = a.generator.timing_glitch(
            int(start), int(stop), int(count), float(bpm_range),
            float(exact_bar) if exact_bar is not None else 4.00,
            float(zero_bar) if zero_bar is not None else 4.00
        )
    except Exception as e:
        return make_fail_response('未知错误: ' + str(e))

    return make_success_response(str(arclist))


@bp.route('/chart/offset', methods=['GET','POST'])
def chart_offset():
    if request.method == 'GET':
        aff = request.args.get('aff')
        offset = request.args.get('offset')
    elif request.method == 'POST':
        aff = request.form.get('aff')
        offset = request.form.get('offset')

    try:
        arclist = a.load(aff)
        arclist.offsetto(int(offset))
        if not aff.startswith('AudioOffset'):
            arclist = a.NoteGroup(arclist)
            arclist.pop(0)
    except Exception as e:
        return make_fail_response('未知错误：' + str(e))

    return make_success_response(str(arclist))

