# -*- coding: utf-8 -*-

from flask import Flask, blueprints, jsonify, request, Blueprint, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename
import os
import uuid

from resource.model import dicModel
from ..model.textLibModel import TextLibrary
from ..model.textLibDataModel import TextLibraryData
from resource import db
import datetime
import pandas as pd
import jieba

textLib_api = Blueprint(name="textLib_api", import_name=__name__)
engine = create_engine("mysql+pymysql://root:12345678@127.0.0.1:3306/labserver?charset=utf8")
Session = sessionmaker(bind=engine)

def create_data_table(tb_id):
    tb_name = "rs_textlibrary_data_" + str(tb_id)
    create_sql = 'CREATE TABLE IF NOT EXISTS {}(' \
                 'id int(11) not null primary key auto_increment,' \
                 'title varchar(255),' \
                 'summary text,' \
                 'keywords varchar(255),' \
                 'publish_time datetime,' \
                 'author varchar(255),' \
                 'source varchar(255),' \
                 'page varchar(20),' \
                 'content text,' \
                 'url varchar(512),' \
                 'publish_source varchar(255),' \
                 'create_time datetime,' \
                 'is_delete int(11)' \
                 ') ENGINE=InnoDB DEFAULT CHARSET=utf8;'.format(tb_name)
    db.session.execute(create_sql)


@textLib_api.route("/test")
def test():
    create_data_table(2)
    return "well done"


@textLib_api.route("", methods=["post"])
def create_text_lib():
    params = request.json
    name = params["name"]
    desc = params["desc"]
    uid = g.uid
    text_lib = TextLibrary(textlibrary_name=name, description=desc, create_user=uid,
                           create_time=datetime.datetime.now())
    try:
        db.session.add(text_lib)
        db.session.commit()
        db.session.flush()
        # 输出新插入数据的主键
        text_lib_id = text_lib.id
        # 创建对应的文本库数据表
        create_data_table(text_lib_id)
        return jsonify(code=20000, flag=True, message="创建文本库成功")
    except:
        return jsonify(code=20001, flag=False, message="创建文本库失败")


@textLib_api.route("/<id>", methods=["put"])
def modify_text_lib(id):
    params = request.json
    text_lib = TextLibrary.query.get(id)
    if text_lib:
        try:
            text_lib.textlibrary_name = params["name"]
            text_lib.description = params["desc"]
            db.session.commit()
            return jsonify(code=20000, flag=True, message="文本库信息修改成功")
        except:
            return jsonify(code=20002, flag=False, message="修改文本库信息失败")
    else:
        return jsonify(code=20001, flag=False, message="未找到该文本库")


@textLib_api.route("/<page>/<size>", methods=["GET"])
def get_text_libs(page=1, size=10):
    try:
        libs = TextLibrary.query.filter(TextLibrary.is_delete != 1).all()
        start = (int(page) - 1) * int(size)
        end = min(int(page) * int(size), len(libs))
        libs_json = []
        for lib in libs[start:end]:
            libs_json.append(lib.as_dict())
        return jsonify(code=20000, flag=True, message="查询成功", data={"total": len(libs), "rows": libs_json})
    except Exception as e:
        print(e)
        return jsonify(code=20001, flag=False, message="未找到文本库信息")


@textLib_api.route("/<id>", methods=["delete"])
def delete_text_lib(id):
    try:
        # 删除文本库
        text_lib = TextLibrary.query.get(id)
        text_lib.is_delete = 1
        text_lib.delete_time = datetime.datetime.now()
        db.session.commit()
        # 删除对应的文本库数据
        # table_name = "rs_textlibrary_data_" + str(id)
        # delete_sql = "update " + table_name + " set is_delete=1 where id=" + id
        # TextLibraryData.__table__.name = table_name
        # text_lib_all_data = TextLibraryData.query.all()
        # for data in text_lib_all_data:
        #     data.is_delete = 1
        #     db.session.commit()
        return jsonify(code=20000, flag=True, message="删除成功")
    except:
        return jsonify(code=20001, flag=False, message="删除失败")


@textLib_api.route("/<lib>/<page>/<size>", methods=["get"])
def get_text_lib_all_data(lib, page, size):
    try:
        table_name = "rs_textlibrary_data_" + str(lib)
        TextLibraryData.__table__.name = table_name
        res = TextLibraryData.query.filter(TextLibraryData.is_delete != 1).all()
        start = (int(page) - 1) * int(size)
        end = min(int(page) * int(size), len(res))
        data_json = []
        for data in res[start:end]:
            data_json.append(data.as_dict())
        return jsonify(code=20000, flag=True, message="查询成功", data={"total": len(res), "rows": data_json})
    except:
        return jsonify(code=20001, flag=False, message="查询失败")


@textLib_api.route('/<lib>', methods=['POST'])
def add_text_lib_data(lib):
    # 打开对应的文本库数据表
    table_name = "rs_textlibrary_data_" + str(lib)
    TextLibraryData.__table__.name = table_name
    # 保存文件
    try:
        upload_file = request.files['data']
        file_name = str(lib) + "_" + str(uuid.uuid1()) + secure_filename(upload_file.filename)
        print(file_name)
        if upload_file is None:
            return jsonify(code=20001, flag=False, message="data_file is null")
        upload_path = os.path.join(os.path.abspath('..'), 'PetrarchChineseServer', 'article', file_name)
        print(upload_path)
        upload_file.save(upload_path)
    except Exception as e:
        return jsonify(code=20002, flag=False, message="上传文件出错")
    # 处理文件
    success_item = 0
    message = None
    try:
        title = request.form.get("title")
        summary = request.form.get("summary")
        keywords = request.form.get("keywords")
        publish_time = request.form.get("publish_time")
        author = request.form.get("author")
        content = request.form.get("content")
        url = request.form.get("url")
        df = pd.read_excel(upload_path)
        all_data = df.loc[:, [title, summary, keywords, publish_time, author, content, url]].values
        for data in all_data:
            print len(data[5])
            insertSQL = "insert into " + table_name + "(title,summary,keywords,publish_time,author,content,url,create_time,is_delete) values('" \
                        + data[0] + "','" + data[1] + "','" + data[2] + "','" + \
                        str(pd.Timestamp(data[3], tz=None).to_pydatetime()) + "','" + data[4] + "','" +\
                        data[5] + "','" + data[6] + "','" + str(datetime.datetime.now())+"','"+str(0)+"')"
            insertSQL = insertSQL.replace(r'"', r'\"')
            insertSQL = insertSQL.replace(r'\u', r'\\u')
            # new_article = TextLibraryData(title=data[0], summary=data[1], keywords=data[2],
            #                               publish_time=pd.Timestamp(data[3], tz=None).to_pydatetime(), author=data[4],
            #                               content=data[5], url=data[6], create_time=datetime.datetime.now())
            # db.session.add(new_article)
            db.session.execute(insertSQL)
            db.session.commit()
            success_item += 1
        message =  jsonify(code=20000, flag=True, message="成功导入" + str(success_item) + "条数据")
    except Exception as e:
        message =  jsonify(code=20003, flag=False, message="文本库导入数据出错")
    finally:
        session = Session()
        tectLib = session.query(TextLibrary).get(lib)
        print lib
        tectLib.line_no = tectLib.line_no + success_item
        tectLib.import_status = 0 if tectLib.line_no == 0 else 1
        session.commit()
        return message



@textLib_api.route("/<lib>/<id>", methods=["put"])
def modify_text_lib_data(lib, id):
    try:
        params = request.json
        table_name = "rs_textlibrary_data_" + str(lib)
        TextLibraryData.__table__.name = table_name
        data = TextLibraryData.query.get(id)
        data.title = params["title"]
        data.summary = params["summary"]
        data.author = params["author"]
        data.url = params["url"]
        db.session.commit()
        return jsonify(code=20000, flag=True, message="文本库数据修改成功")
    except Exception as e:
        return jsonify(code=20001, flag=False, message="修改文本库数据失败")


@textLib_api.route("/<lib>/<id>", methods=["delete"])
def delete_text_lib_data(lib, id):
    try:
        table_name = "rs_textlibrary_data_" + str(lib)
        delete_sql = "update " + table_name + " set is_delete=1 where id=" + id
        # TextLibraryData.__table__.name = table_name
        # data = TextLibraryData.query.get(id)
        # data.is_delete = 1
        # db.session.commit()
        db.session.execute(delete_sql)
        db.session.commit()
        lib = TextLibrary.query.get(lib)
        lib.line_no = lib.line_no - 1
        lib.import_status = 0 if lib.line_no == 0 else 1
        db.session.commit()
        return jsonify(code=20000, flag=True, message="删除文本库数据成功")
    except Exception as e:
        return jsonify(code=20001, flag=False, message="删除文本库数据失败")


@textLib_api.route("/data/<lib>/<id>", methods=["get"])
def get_text_lib_data(lib, id):
    try:
        table_name = "rs_textlibrary_data_" + str(lib)
        TextLibraryData.__table__.name = table_name
        data = TextLibraryData.query.get(id)
        # format content
        data_dict = data.as_dict()
        paragraphs = data.content.decode("utf-8").split(u"\u3000")
        # remove the empty str
        paragraphs = filter(None, paragraphs)
        res = []
        for p in paragraphs:
            p = '\t' + p
            res.append(p)
        data_dict.update({"content":res})
        # get words cloud
        content = data.content
        # trash_set
        trash_set = {u"，", u"。", u"”", u"“", u"（", u"）", u"(", u")", u"！", u"？", u" ",u"、",u"《",u"》"}

        words_list = list(jieba.cut(content))
        words_set = set(words_list) - trash_set
        words_dict = {}
        for word in words_set:
            words_dict[word] = words_list.count(word)

        # 对词频进行排序
        words_list_sorted = list(words_dict.items())
        words_list_sorted.sort(key=lambda e: e[1], reverse=True)
        top_word_num = 0
        list_rs = []
        max_size = words_list_sorted[0][1]
        rate = 100/max_size
        for topWordTup in words_list_sorted:
            if top_word_num == 40:
                break
            list_rs.append({"text": topWordTup[0], "size": topWordTup[1]*rate})
            top_word_num += 1
        return jsonify(code=20000, flag=True, message="查询成功", data={"data": data_dict, "cloud": list_rs})
    except Exception as e:
        return jsonify(code=20001, flag=False, message="查询失败")


@textLib_api.route("/related/<lib>/<id>", methods=["get"])
def get_related_data(lib, id):
    try:
        table_name = "rs_textlibrary_data_" + str(lib)
        TextLibraryData.__table__.name = table_name
        all_data = TextLibraryData.query.filter(TextLibrary.is_delete != 1).all()
        data_json = []
        for data in all_data:
            if data.id != int(id):
                data_json.append(data.as_dict())
        return jsonify(code=20000, flag=True, message="查询成功", data=data_json)
    except Exception as e:
        return jsonify(code=20001, flag=False, message="查询失败")
