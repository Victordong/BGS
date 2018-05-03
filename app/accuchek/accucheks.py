from app.accuchek import accuchek_blueprint
from app import db
from flask import request, jsonify, url_for, current_app
from app.models import Accuchek
from sqlalchemy.exc import OperationalError,IntegrityError
from flask_login import login_required
import json

def std_json(d):
    r = {}
    for k, v in d.items():
        r[k] = json.loads(v)
    return r

@accuchek_blueprint.route('/accucheks', methods=['GET'])
@login_required
def get_accucheks():
    fields = [i for i in Accuchek.__table__.c._data]
    accunckes = Accuchek.query
    limit = None
    per_page = current_app.config['PATIENTS_PRE_PAGE']
    for k, v in std_json(request.args).items():
        if k in fields:
            accunckes = accunckes.filter_by(**{k: v})
        if k == 'per_page':
            per_page = v
        if k == 'limit':
            limit = v
    accunckes = accunckes.limit(limit).from_self() if limit is not None else accunckes.from_self()
    page = request.args.get('page', 1, type=int)
    pagination = accunckes.paginate(page, per_page=per_page, error_out=False)
    accunckes = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('accuchek_blueprint.get_accucheks', page=page - 1)
    next = None
    if pagination.has_next:
        next = url_for('accuchek_blueprint.get_accucheks', page=page + 1)
    return jsonify({
        'accucheks': [accuncke.to_json() for accuncke in accunckes],
        'prev': prev,
        'next': next,
        'has_prev':pagination.has_prev,
        'has_next':pagination.has_next,
        'total': pagination.total,
        'pages': pagination.pages,
        'per_page': per_page,
        'status': 'success',
        'reason': 'there are datas'
    })

"""
@api {GET} /accucheks 获取所有血糖仪信息(地址栏筛选)
@apiGroup accucheks
@apiName 获取所有血糖仪信息

@apiParam (params) {String} sn 血糖仪sn码
@apiParam (params) {Number} bed_id 病床号码
@apiParam (params) {Number} limit 查询总数量
@apiParam (params) {Number} per_page 每一页的数量
@apiParam (Login) {String} login 登录才可以访问

@apiSuccess {Array} accucheks 返回所有根据条件查询到的血糖仪信息

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "accuncheks":[{
            "accuchek_id":"血糖仪id",
            "sn":"血糖仪sn码",
            "bed_id":"床位号"
        }](血糖仪信息),
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

@accuchek_blueprint.route('/accucheks', methods = ['POST'])
@login_required
def new_accuchek():
    accuchek = Accuchek()
    if 'sn' in request.json:
        sn = request.json['sn']
        may_accuchek = Accuchek.query.filter(Accuchek.sn == sn).first()
        if may_accuchek:
            return jsonify({
                'status': 'fail',
                'reason': 'the sn has been used'
            })
    else:
        return jsonify({
            'status': 'fail',
            'reason': 'there is no sn'
        })
    for k in request.json:
        if hasattr(accuchek, k):
            try:
                setattr(accuchek, k, request.json[k])
            except IntegrityError as e:
                return jsonify({
                    'status': 'fail',
                    'reason': e
                })
    try:
        db.session.add(accuchek)
        db.session.commit()
    except OperationalError as e:
        return jsonify({
            'status': 'fail',
            'reason': e,
            'data': accuchek.to_json()
        })
    return jsonify({
        "accukces": [accuchek.to_json()],
        "status": "success",
        "reason": "the data has been added"
    })

"""
@api {POST} /accucheks 添加一个新的血糖仪(json数据)
@apiGroup accucheks
@apiName 添加一个血糖仪

@apiParam (params) {String} sn 血糖仪sn码
@apiParam (params) {Number} bed_id 病床号码
@apiParam (Login) {String} login 登录才可以访问 

@apiSuccess {Array} accucheks 返回添加血糖仪的信息

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "accucheks":[{
            "bed_id":"床位号",
            "sn":"血糖仪sn码",
            "accuchek_id":"血糖仪id"   
        }],
        "status":"success",
        "reason":"the data has been added"
    }
    {
        "status":"fail",
        "reason":"失败原因"
    }
"""

@accuchek_blueprint.route('/accucheks/<int:id>')
@login_required
def get_accuchek(id):
    accuchek = Accuchek.query.get_or_404(id)
    return jsonify({
        "accukces":[accuchek.to_json()],
        "status":"success",
        "reason":"there is the data"
    })

"""
@api {GET} /accucheks/<int:id> 根据id获取血糖仪信息
@apiGroup accucheks
@apiName 根据id获取血糖仪信息

@apiParam (params) {Number} id 血糖仪id
@apiParam (Login) {String} login 登录才可以访问

@apiSuccess {Array} accucheks 返回相应血糖仪的信息

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "accucheks":[{
            "bed_id":"床位号",
            "sn":"血糖仪sn码",
            "accuchek_id":"血糖仪id"   
        }],
        "status":"success",
        "reason":"there is the data"
    }

@apiError (Error 4xx) 404 对应id的血糖仪不存在

@apiErrorExample Error-Resopnse:
    HTTP/1.1 404 对应的血糖仪信息不存在
    {
       "error": "not found",
        "reason": "404 Not Found: The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.",
        "status": "fail" 
    }
"""

@accuchek_blueprint.route('/accucheks/<int:id>', methods = ['DELETE'])
@login_required
def delete_accuchek(id):
    accuchek = Accuchek.query.get_or_404(id)
    try:
        db.session.delete(accuchek)
        db.session.commit()
    except OperationalError as e:
        return jsonify({
            'status':'fail',
            'reason':e
        })
    return jsonify({
        "accukces": [accuchek.to_json()],
        "status": "success",
        "reason": "the data has been deleted"
    })

"""
@api {DELETE} /accucheks/<int:id> 删除id所代表的血糖仪
@apiGroup accucheks
@apiName 删除id所代表的血糖仪

@apiParam (params) {Number} id 血糖仪id
@apiParam (Login) {String} login 登录才可以访问

@apiSuccess {Array} accucheks 返回被删除的血糖仪的信息

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "accucheks":[{
            "bed_id":"床位号",
            "sn":"血糖仪sn码",
            "accuchek_id":"血糖仪id"   
        }],
        "status":"success",
        "reason":"the data has been deleted"
    }

@apiError (Error 4xx) 404 对应id的血糖仪不存在

@apiErrorExample Error-Resopnse:
    HTTP/1.1 404 对应的血糖仪信息不存在
"""

@accuchek_blueprint.route('/accucheks/<int:id>', methods = ['PUT'])
@login_required
def change_accuchek(id):
    accuchek = Accuchek.query.get_or_404(id)
    if 'sn' in request.json:
        sn = request.json['sn']
        may_accuchek = Accuchek.query.filter(Accuchek.sn == sn).first()
        if may_accuchek is not None and may_accuchek.accuchek_id != id:
            return jsonify({
                'status':'fail',
                'reason':'the sn has been used'
            })
    for k in request.json:
        if hasattr(accuchek, k):
            setattr(accuchek, k, request.json[k])
    try:
        db.session.add(accuchek)
        db.session.commit()
    except OperationalError as e:
        return jsonify({
            'status':'fail',
            'reason':e
        })
    return jsonify({
        "accukces": [accuchek.to_json()],
        "status": "success",
        "reason": "the data has been changed"
    })

"""
@api {PUT} /accucheks/<int:id> 更改id所代表的血糖仪的信息(json数据)
@apiGroup accucheks
@apiName 更改id所代表的血糖仪的信息

@apiParam (params) {Number} id 血糖仪id
@apiParam (Login) {String} login 登录才可以访问

@apiSuccess {Array} accucheks 返回更改后的血糖仪的信息

@apiSuccessExample Success-Response:
    HTTP/1.1 200 OK
    {
        "accucheks":[{
            "bed_id":"床位号",
            "sn":"血糖仪sn码",
            "accuchek_id":"血糖仪id"   
        }],
        "status":"success",
        "reason":"the data has been changed"
    }


@apiError (Error 4xx) 404 对应id的血糖仪不存在

@apiErrorExample Error-Resopnse:
    HTTP/1.1 404 对应的血糖仪信息不存在
"""

