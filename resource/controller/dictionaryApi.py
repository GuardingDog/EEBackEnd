# -*- coding: utf-8 -*-

from flask import request, Blueprint, jsonify, current_app, make_response, send_file
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
import hashlib
from ..model import userModel,dicModel
from resource import app
from resource import db
from werkzeug.utils import secure_filename
import datetime
import os

dictionary_api = Blueprint(name="dictionary_api", import_name=__name__)


@dictionary_api.route('/test', methods=['POST'])
def test():
    return "sssss"


@dictionary_api.route('', methods=['POST'])
def add_dic():
    try:
        upload_file = request.files['dic']
        name = request.form.get('name')
        file_name = secure_filename(upload_file.filename)
        print(file_name)
        if upload_file is None:
            return jsonify(code=20001, flag=False, message="dic_file is null")
        upload_path = os.path.join(os.path.abspath('..'), 'PetrarchChineseServer','dictionary',file_name)
        print(upload_path)
        upload_file.save(upload_path)
        dictionary=dicModel.Dictionary(name=name,file_name=file_name,create_user=2,create_time=datetime.datetime.now())
        db.session.add(dictionary)
        db.session.commit()
        return jsonify(code=20000, flag=True, message="成功添加词典")
    except Exception as e:
        return jsonify(code=20001, flag=False, message="添加词典失败")


@dictionary_api.route('/<id>', methods=['DELETE'])
def del_dic(id):
    dictionary=dicModel.Dictionary.query.get(id)
    if dictionary is None:
        return jsonify(code=20001, flag=False, message="要删除的词典不存在")
    db.session.delete(dictionary)
    db.session.commit()
    return jsonify(code=20000, flag=True, message="删除成功")


@dictionary_api.route('/data/<id>', methods=['GET'])
def get_dic(id):
    dictionary = dicModel.Dictionary.query.filter_by(id=id).first()
    print(dictionary)
    #dictionary=dicModel.Dictionary.query.get(id)
    if dictionary is None:
        return jsonify(code=20001, flag=False, message="要查找的词典不存在")
    file_name=dictionary.file_name
    file_path = os.path.join(os.path.abspath('..'), 'PetrarchChineseServer','dictionary',file_name)
    print file_path
    with open(file_path,'r') as f:
        content = f.readlines()
    content_str = ""
    for line in content:
        content_str+=line
    return jsonify({'code': 20000,'flag':True, 'message':"get_dictionary sucessful",'data':{"content":content_str}})


@dictionary_api.route("<page>/<size>", methods=["get"])
def get__all_dict(page, size):
    try:
        res = dicModel.Dictionary.query.all()
        start = (int(page) - 1) * int(size)
        end = min(int(page) * int(size), len(res))
        data_json = []
        for data in res[start:end]:
            data_json.append(data.as_dict())
        return jsonify(code=20000, flag=True, message="查询成功", data={"total": len(res), "rows": data_json})
    except Exception as e:
        return jsonify(code=20001, flag=False, message="查询失败")


@dictionary_api.route("/download/<id>",methods=["get"])
def download(id):
    dictionary = dicModel.Dictionary.query.filter_by(id=id).first()
    if dictionary is None:
        return jsonify(code=20001, flag=False, message="要下载的词典不存在")
    file_name = dictionary.file_name
    file_path = os.path.join(os.path.abspath('..'), 'PetrarchChineseServer', 'dictionary', file_name)
    # 首先定义一个生成器，每次读取512个字节
    return send_file(file_path)

# return 'xx [---] '
def get_event_code(event):
    event_array = event.split(" ")
    temp_str = ""
    temp_str += event_array[0]
    temp_str += " ["
    if len(event_array) > 1:
        temp_str += event_array[1] + "]"
    else:
        temp_str += "---] "
    return temp_str.encode("utf-8")

@dictionary_api.route("/self",methods=["post"])
def create_dictionary_self():
    """
    json
    {
        name: "dict_name",
        words:[{main:"main_name",same:"a1 a2 a3"}],
        events:[{main:"main_name 010",same:"a1 020, a2 030",slave:[{value:"name 040",select:"1/新增(2/选择)"}]
    }
    """
    try:
        params = request.json
        diction_name = params["name"]
        words = params["words"]
        events = params["events"]
        result_str = []
        # synonym sets
        result_str.append("####### SYNONYM SETS #######")
        result_str.append("")
        for word in words:
            main_word = word["main"]
            result_str.append("&"+main_word)
            same_words = word["same"].split(" ")
            for same_word in same_words:
                result_str.append("+"+same_word)
            result_str.append("")
        result_str.append("")
        # verbs patterns
        result_str.append("####### VERB PATTERNS #######")
        result_str.append("")
        for event in events:
            verb = event["main"]
            same_verb = event["same"]
            verb_slaves = event["slave"]
            temp_str = "--- "
            temp_str += get_event_code(verb) + "---"
            result_str.append(temp_str)
            same_verbs = same_verb.split(",")
            for same in same_verbs:
                s = same.strip()
                result_str.append(get_event_code(s))
            for slave in verb_slaves:
                temp_str = "- * "
                if int(slave["select"]) == 2:
                    temp_str += "&"
                temp_str += get_event_code(slave["value"])
                result_str.append(temp_str)
            for i in range(4):
                result_str += ""
        upload_path = os.path.join(os.path.abspath('..'), 'PetrarchChineseServer', 'dictionary', diction_name+".txt")
        print upload_path
        with open(upload_path,"w") as f:
            f.write("\n".join(result_str))
        # write in db
        dictionary = dicModel.Dictionary(name=diction_name, file_name=diction_name+".txt", create_user=2,
                                         create_time=datetime.datetime.now())
        db.session.add(dictionary)
        db.session.commit()
        return jsonify(code=20000, flag=True, message="字典创建成功")
    except Exception as e:
        return jsonify(code=20001, flag=False, message="新建字典失败")

