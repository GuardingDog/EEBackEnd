# -*- coding: utf-8 -*-

from flask import request, Blueprint,jsonify,current_app,g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
import hashlib
from ..model import userModel
from resource import app
from resource import db
import datetime


user_api = Blueprint(name="user_api", import_name=__name__)


def spw(password):
    md5=hashlib.md5()
    md5.update(password.encode())
    return md5.hexdigest()


def create_token(api_user):
    s = Serializer(current_app.config["SECRET_KEY"], expires_in=current_app.config["EXPIRES_IN"])
    # 接收用户id转换与编码
    token = s.dumps({"id": api_user}).decode("ascii")
    return token


def verify_token(token):
    # 参数为私有秘钥，跟上面方法的秘钥保持一致
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        # 转换为字典
        data = s.loads(token)
    except BaseException:
        return "登录未授权"
    except SignatureExpired:
        return "登录已过期"
    uid = data["id"]
    return uid


@app.before_request
def is_login():
    if request.path == "/user/login" or request.path == "/user/register" :
        return None
    token = request.headers.get("Authorization")
    if token:
        uid = verify_token(token)
        if type(uid) is int:
            g.uid = uid
        else:
            return jsonify(code=20002, flag=False, message=uid)
    else:
        return jsonify(code=20001,flag=False,message="请先登录")


@user_api.route('/register', methods=['post'])
def register():
    params = request.json
    username = params["username"]
    password = params["password"]
    if username and password:
        if userModel.User.query.filter_by(name=username).first():
            return jsonify(code=20001, flag=False, message="该账号已存在")
        user = userModel.User(name=username, password=spw(password), nickname="admin",create_time=datetime.datetime.now())
        db.session.add(user)
        db.session.commit()
        return jsonify(code=20000, flag=True, message="注册成功")
    return jsonify(code=20002, flag=False, message="未填写登录信息")


@user_api.route('/login', methods=['POST'])
def login():
    params = request.json
    username = params["username"]
    password = params["password"]
    user = userModel.User.query.filter_by(name=username).first()
    if user is not None:
        if spw(password) == user.password:
            token = create_token(user.id)
            data={}
            data.update({"token":token})
            print(token)
            return jsonify(code=20000, flag=True, message="登录成功", data=data)
        return jsonify(code=20002, flag=False, message="密码输入错误")
    return jsonify(code=20001, flag=False, message="该账户不存在")


@user_api.route('/test')
def test():
    uid = g.uid
    return "fine:"+ str(uid)
