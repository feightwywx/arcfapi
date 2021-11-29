#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# (c)2021 .direwolf <kururinmiracle@outlook.com>
# Licensed under the MIT License.

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


@bp.route('/arc/splitbytiming', methods=['GET'])
def arc_split_by_timing():
    arc = request.args.get('arc')
    timings = request.args.get('timings')

    arc_obj = a.loadline(arc)
    if not isinstance(arc_obj, a.Arc):
        return make_fail_response(''.join('Invalid Arc string: ', arc))
    timings_obj = a.load(timings)

    result = a.generator.arc_slice_by_timing(arc_obj, timings_obj)

    return make_success_response(str(result))


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


@bp.route('/arc/construct', methods=['GET'])
def arc_construct():
    start = int(request.args.get('start'))
    stop = int(request.args.get('stop'))
    start_x = float(request.args.get('start_x'))
    stop_x = float(request.args.get('stop_x'))
    start_y = float(request.args.get('start_y'))
    stop_y = float(request.args.get('stop_y'))
    easing = request.args.get('easing')
    color = int(request.args.get('color'))
    skyline = request.args.get('skyline')
    if skyline == 'true':
        skyline = True
    elif skyline == 'false':
        skyline = False
    else:
        return make_fail_response(''.join(['Invalid skyline value: ', skyline]))
    arctap = request.args.get('arctap')
    if arctap is not None:
        arctap = arctap.split(',')

    try:
        arc = a.Arc(start, stop, start_x, stop_x, easing, start_y, stop_y, color, skyline, arctap)
    except Exception as e:
        return make_fail_response('未知错误: ' + str(e))
    
    return make_success_response(str(arc))


@bp.route('/arc/animate', methods=['GET'])
def arc_animate():
    arc = request.args.get('arc')
    arc = a.loadline(arc)
    if not isinstance(arc, a.Arc):
        return make_fail_response(''.join('Invalid Arc string: ', arc))
    start = int(request.args.get('start'))
    stop = int(request.args.get('stop'))
    delta_x = float(request.args.get('delta_x'))
    delta_y = float(request.args.get('delta_y'))
    basebpm = float(request.args.get('basebpm'))
    easing_x = request.args.get('easing_x')
    easing_b_point_x = request.args.get('easing_b_point_x')
    if not easing_x:
        easing_x = 's'
    elif easing_x == 'b':  # easing_b_point_x转float列表
        if not easing_b_point_x:
            easing_b_point_x = [1/3, 0, 2/3, 1]
        else:
            easing_b_point_x = easing_b_point_x.split(',')
            easing_b_point_x = list(map(lambda x: float(x), easing_b_point_x))
    easing_y = request.args.get('easing_y')
    easing_b_point_y = request.args.get('easing_b_point_y')
    if not easing_y:
        easing_y = 's'
    elif easing_y == 'b':  # easing_b_point_y转float列表
        if not easing_b_point_y:
            easing_b_point_y = [1/3, 0, 2/3, 1]
        else:
            easing_b_point_y = easing_b_point_y.split(',')
            easing_b_point_y = list(map(lambda x: float(x), easing_b_point_y))
    infbpm = float(request.args.get('infbpm')) if request.args.get('infbpm') else 999999.0
    framerate = float(request.args.get('framerate')) if request.args.get('framerate') else 60.0
    fake_note_t = int(request.args.get('fake_note_t')) if request.args.get('fake_note_t') else 100000
    offset_t = int(request.args.get('offset_t')) if request.args.get('offset_t') else 0
    delta_offset_t = int(request.args.get('delta_offset_t')) if request.args.get('delta_offset_t') else 0
    easing_offset_t = request.args.get('easing_offset_t')
    easing_b_point_offset_t = request.args.get('easing_b_point_offset_t')
    if not easing_offset_t:
        easing_offset_t = 's'
    elif easing_offset_t == 'b':  # easing_b_point_offset_t转float列表
        if not easing_b_point_offset_t:
            easing_b_point_offset_t = [1/3, 0, 2/3, 1]
        else:
            easing_b_point_offset_t = easing_b_point_offset_t.split(',')
            easing_b_point_offset_t = list(map(lambda x: float(x), easing_b_point_offset_t))

    count = (stop - start) / 1000 * framerate
    if count > 1024:
        return make_fail_response('细分数量过大（最大支持1024细分）')
    
    result = a.generator.arc_animation_assist(
        arc, start, stop, delta_x, delta_y, basebpm, easing_x,easing_b_point_x, easing_y, easing_b_point_y, infbpm, framerate, fake_note_t, offset_t, delta_offset_t, easing_offset_t, easing_b_point_offset_t
    )

    return make_success_response(str(result))



@bp.route('/arc/rain', methods=['GET'])
def arc_rain():
    start = request.args.get('start')
    stop = request.args.get('stop')
    step = request.args.get('step')
    length = request.args.get('length')

    count = (int(stop) - int(start)) / float(step)
    if count > 512:
        return make_fail_response('细分数量过大（最大支持512细分）')

    try:
        arclist = a.generator.arc_rain(int(start), int(stop), float(step), float(length) if length is not None else None)
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
    easing_mode = request.args.get('easing')
    easing_b_point = request.args.get('easing_b_point')
    if not easing_mode:
        easing_mode = 's'
    elif easing_mode == 'b':  # easing_b_point转float列表
        if not easing_b_point:
            easing_b_point = [1/3, 0, 2/3, 1]
        else:
            easing_b_point = easing_b_point.split(',')
            easing_b_point = list(map(lambda x: float(x), easing_b_point))

    if int(count) > 512:
        return make_fail_response('细分数量过大（最大支持512细分）')

    try:
        arclist = a.generator.timing_easing(
            int(start), int(stop), float(start_bpm), float(stop_bpm), int(count),
            float(bar) if bar is not None else 4.00, easing_mode, easing_b_point
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


@bp.route('/chart/align', methods=['GET','POST'])
def chart_align():
    if request.method == 'GET':
        aff = request.args.get('aff')
        bpm = request.args.get('bpm')
        error = request.args.get('error')
        lcd = request.args.get('lcd')
    elif request.method == 'POST':
        aff = request.form.get('aff')
        bpm = request.form.get('bpm')
        error = request.form.get('error')
        lcd = request.form.get('lcd')

    try:
        arclist = a.load(aff)
        arclist.align(
            float(bpm), int(error), int(lcd)
        )
    except Exception as e:
        return make_fail_response('未知错误：' + str(e))
    
    return make_success_response(str(arclist))

@bp.route('/chart/mirror', methods=['GET','POST'])
def chart_mirror():
    if request.method == 'GET':
        aff = request.args.get('aff')
    elif request.method == 'POST':
        aff = request.form.get('aff')
    
    try:
        arclist = a.load(aff)
        arclist.mirror()
    except Exception as e:
        return make_fail_response('未知错误：' + str(e))

    return make_success_response(str(arclist))
