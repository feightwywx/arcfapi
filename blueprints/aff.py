#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# (c)2021 .direwolf <kururinmiracle@outlook.com>
# Licensed under the MIT License.
import json

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
                'info': '传入值为空或者无效'
            }
    except aex.AffNoteValueError as e:
        return {
            'status': 'fail',
            'info': 'Note数值非法: ' + str(e)
        }
    except Exception as e:
        return {
            'status': 'fail',
            'info': '未知错误: ' + str(e)
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
            'code': 500,
            'info': '传入值不是Arc的表达式: ' + arcstring
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
    if 'step' in paradict:
        step = int((stop - start) / int(paradict['step']))
    else:
        step = None
    print('step is:', step)

    return str(a.NoteGroup(arcobj[start:stop:step]))
