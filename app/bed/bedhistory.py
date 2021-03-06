from app.bed import bed_blueprint
from app import db
from flask import request, jsonify, url_for, current_app
from app.models import BedHistory
from sqlalchemy.exc import IntegrityError
from app.models import InvalidUsage
import datetime
from flask_login import login_required
import json
from app.form_model import BedHistoryValidation, GetBedHistoryValidation, ChangeBedHistoryValidation
from marshmallow.exceptions import ValidationError

def std_json(d):
    r = {}
    for k, v in d.items():
        try:
            r[k] = json.loads(v)
        except:
            r[k] = v
    return r

@bed_blueprint.route('/bed_historys')
@login_required
def get_histories():
    params_dict = {
        'history_id': request.args.get('history_id', None, type=int),
        'sn': request.args.get('sn', None, type=str),
        'id_number': request.args.get('id_number', None, type=str),
        'time': request.args.get('time', None, type=str),
        'date': request.args.get('date', None, type=str),
        'bed_id': request.args.get('bed_id', None, type=int),
        'limit': request.args.get('limit', None, type=int),
        'page': request.args.get('page', None, type=int),
        'patient_id': request.args.get('patient_id', None, type=int),
        'per_page': request.args.get('per_page', None, type=int)
    }
    try:
        GetBedHistoryValidation().load(params_dict)
    except ValidationError as e:
        return jsonify({
            'status': 'fail',
            'reason': str(e)
        })
    fields = [i for i in BedHistory.__table__.c._data]
    bed_historys = BedHistory.query.order_by(BedHistory.date.desc(), BedHistory.time.desc())
    per_page = current_app.config['PATIENTS_PRE_PAGE']
    limit = None
    for k, v in std_json(request.args).items():
        if k in fields:
            bed_historys = bed_historys.filter_by(**{k: v})
        if k == 'per_page':
            per_page = v
        if k == 'limit':
            limit = v
    bed_historys = bed_historys.limit(limit).from_self() if limit is not None else bed_historys.from_self()
    page = request.args.get('page', 1, type=int)
    pagination = bed_historys.paginate(page, per_page=per_page, error_out=False)
    bed_historys = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('bed_blueprint.get_histories', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('bed_blueprint.get_histories', page=page + 1)
    return jsonify({
        'bed_historys': [bed_history.to_json() for bed_history in bed_historys],
        'prev': prev,
        'next': next,
        'has_prev':pagination.has_prev,
        'has_next':pagination.has_next,
        'total': pagination.total,
        'pages': pagination.pages,
        'per_page': per_page,
        'status': 'success',
        'reason': '这里是所有的数据'
    })

"""

@api {GET} /bed_historys 获取筛选所有的床位历史信息
@apiGroup bed_historys

@apiParam (params) {Int} bed_id 床位id
@apiParam (params) {Int} patient_id 患者id
@apiParam (params) {String} date 床位历史日期_日期格式(0000-00-00)
@apiParam (params) {String} time 床位历史时间_时间模式(00:00:00)
@apiParam (params) {String} id_number 医疗卡号
@apiParam (params) {String} sn 血糖仪sn码
@apiParam (params) {Int} limit 查询总数量
@apiParam (params) {Int} per_page 每一页的数量
@apiParam (params) {Int} page 查询页数
@apiParam (Login) {String} login 登录才可以访问

@apiSuccess {Array} bed_historys 返回筛选过的床位历史信息信息

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "bed_historys":[{
            "history_id":"历史信息id",
            "bed_id":"床位号",
            "time":"历史信息时间",
            "date":"历史信息日期",
            "sn":"血糖仪sn码",
            "id_number":"医疗卡号",
            "patient_id":"患者id"
        }],
        "prev":"上一页地址",
        "next":"下一页地址",
        'has_prev':'是否有上一页',
        'has_next':'是否有下一页',
        'total': '查询总数量',
        'pages': '查询总页数',
        'per_page': '每一页的数量',
        'status': 'success',
        'reason': 'there are datas'
    }
"""


@bed_blueprint.route('/bed_historys', methods = ['POST'])
@login_required
def new_history():
    params_dict = {
        'history_id': request.json.get('history_id', None),
        'sn': request.json.get('sn', None),
        'id_number': request.json.get('id_number', None),
        'time': request.json.get('time', None),
        'date': request.json.get('date', None),
        'bed_id': request.json.get('bed_id', None),
        'patient_id': request.json.get('patient_id', None)
    }
    try:
        BedHistoryValidation().load(params_dict)
    except ValidationError as e:
        return jsonify({
            'status': 'fail',
            'reason': str(e)
        })
    bed_history = BedHistory()
    for k in request.json:
        if hasattr(bed_history, k):
            setattr(bed_history, k, request.json[k])
    date = datetime.datetime.now().date()
    time = str(datetime.datetime.now().time())[0:8]
    bed_history.date = date
    bed_history.time = time
    try:
        db.session.add(bed_history)
        db.session.commit()
    except IntegrityError as e:
        raise InvalidUsage(message=str(e), status_code=500)
    return jsonify({
        "bed_history":bed_history.to_json(),
        "status":"success",
        "reason":"数据已经被添加"
    })

"""

@api {POST} /bed_historys 新建床位历史信息
@apiGroup bed_historys

@apiParam (json) {Int} bed_id 床位id
@apiParam (json) {Date} date 床位历史日期_日期格式(0000-00-00)
@apiParam (json) {Time} time 床位历史时间_时间模式(00:00:00)
@apiParam (json) {String} id_number 医疗卡号
@apiParam (json) {String} sn 血糖仪sn码
@apiParam (Login) {String} login 登录才可以访问

@apiSuccess {Array} bed_historys 返回新建的床位历史信息

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "bed_history":{
            "history_id":"历史信息id",
            "bed_id":"床位号",
            "time":"历史信息时间",
            "date":"历史信息日期",
            "sn":"血糖仪sn码",
            "id_number":"医疗卡号"  
        },
        "status":"success",
        "reason":"the data has been added"
    }

"""


@bed_blueprint.route('/bed_historys/<int:id>')
@login_required
def get_history(id):
    bed_history = BedHistory.query.get_or_404(id)
    return jsonify({
        "bed_history": bed_history.to_json(),
        "status": "success",
        "reason": "这是查询到的数据"
    })

"""

@api {GET} /bed_historys/<int:id> 获取id所代表的床位历史的信息
@apiGroup bed_historys

@apiParam (params) {Int} id 床位历史信息id
@apiParam (Login) {String} login 登录才可以访问

@apiSuccess {Array} bed_historys 返回id所代表的床位历史信息

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "bed_history":{
            "history_id":"历史信息id",
            "bed_id":"床位号",
            "time":"历史信息时间",
            "date":"历史信息日期",
            "sn":"血糖仪sn码",
            "id_number":"医疗卡号"  
        },
        "status":"success",
        "reason":"there is the data"
    }

"""


@bed_blueprint.route('/bed_historys/<int:id>', methods = ['PUT'])
@login_required
def change_history(id):
    params_dict = {
        'history_id': request.json.get('history_id', None),
        'sn': request.json.get('sn', None),
        'id_number': request.json.get('id_number', None),
        'time': request.json.get('time', None),
        'date': request.json.get('date', None),
        'bed_id': request.json.get('bed_id', None),
        'patient_id': request.json.get('patient_id',None)
    }
    try:
        ChangeBedHistoryValidation().load(params_dict)
    except ValidationError as e:
        return jsonify({
            'status': 'fail',
            'reason': str(e)
        })
    bed_history = BedHistory.query.get_or_404(id)
    for k in request.json:
        if hasattr(bed_history, k):
            setattr(bed_history, k ,request.json[k])
    if 'time' in request.json:
        time = request.json['time']
        if len(time)<8:
            time = time[0:5]+':00'
            bed_history.time = time
    try:
        db.session.add(bed_history)
        db.session.commit()
    except IntegrityError as e:
        raise InvalidUsage(message=str(e), status_code=500)
    return jsonify({
        "bed_history": bed_history.to_json(),
        "status": "success",
        "reason": "数据已经被更改了"
    })

"""

@api {PUT} /bed_historys/<int:id> 更改id所代表的床位历史的信息
@apiGroup bed_historys

@apiParam (json) {Int} bed_id 床位id
@apiParam (json) {Int} patient_id 患者id
@apiParam (json) {Date} date 床位历史日期_日期格式(0000-00-00)
@apiParam (json) {Time} time 床位历史时间_时间模式(00:00:00)
@apiParam (json) {String} id_number 医疗卡号
@apiParam (json) {String} sn 血糖仪sn码
@apiParam (params) {Int} id 床位历史信息id
@apiParam (Login) {String} login 登录才可以访问

@apiSuccess {Array} bed_historys 返回更改的床位历史信息

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "bed_history":{
            "history_id":"历史信息id",
            "bed_id":"床位号",
            "time":"历史信息时间",
            "date":"历史信息日期",
            "sn":"血糖仪sn码",
            "id_number":"医疗卡号"  
        },
        "status":"success",
        "reason":"the data has been changed"
    }
    不是主治医师修改
    {
        "status":"fail",
        "reason":"no root"
    }
"""


@bed_blueprint.route('/bed_historys/<int:id>', methods = ['DELETE'])
@login_required

def delete_history(id):
    bed_history = BedHistory.query.get_or_404(id)
    try:
        db.session.delete(bed_history)
        db.session.commit()
    except IntegrityError as e:
        raise InvalidUsage(message=str(e), status_code=500)
    return jsonify({
        "status": "success",
        "reason": "数据已经被删除了"
    })


"""

@api {DELETE} /bed_historys/<int:id> 删除id所代表的床位历史的信息
@apiGroup bed_historys

@apiParam (params) {Int} id 床位历史信息id
@apiParam (Login) {String} login 登录才可以访问

@apiSuccess {Array} status 返回删除的

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "status":"success",
        "reason":"the data has been deleted"
    }
    不是主治医师删除
    {
        "status":"fail",
        "reason":"no root"
    }

"""
