# -*- coding: utf-8 -*-
from resource.model import dicModel
import datetime
import io
import json
from ConfigParser import ConfigParser
import threading
import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from flask import jsonify, request, Blueprint, g
from resource.model.textLibModel import TextLibrary
from petrarch_chinese.main import petrarch_chinese_main
from resource import db
from resource.model.analysisProjectModel import AnalysisProject
from resource.model.analysisProjectResultModel import AnalycisEventResult
from resource.model.textLibDataModel import TextLibraryData
from resource.model.dicModel import Dictionary
from sqlalchemy import text
from resource.model.analysisProjectResultModelSubThread import AnalycisEventResultSubThread

eventLibApi = Blueprint(name='event_lib', import_name=__name__)

engine = create_engine("mysql+pymysql://root:12345678@127.0.0.1:3306/labserver?charset=utf8")
Session = sessionmaker(bind=engine)

threadLock = threading.Lock()
current_project_id = None


def create_analysis_result_table(project_id):
    project_id = str(project_id)
    table_name = 'rs_analysis_event_result_%s' % project_id
    drop_sql = 'DROP TABLE IF EXISTS {}'.format(table_name)
    create_sql = 'create table IF NOT EXISTS {}(' \
                 'id int(20) not null primary key auto_increment,' \
                 'text_id varchar(255) not null,' \
                 'recall_rate decimal(10,2),' \
                 'accuracy_rate decimal(10,2),' \
                 'event_num int(11) not null,' \
                 'event_result text not null' \
                 ')'.format(table_name)
    db.session.execute(drop_sql)
    db.session.execute(create_sql)


@eventLibApi.route('/test')
def test():
    # init_petrarch('1', '1')
    # create_analysis_result_table('100')
    petrarch_chinese_main()
    return 'well done'


class AnalysisThread(threading.Thread):
    def __init__(self, project_id, lib_id, dict_id, algorithm):
        threading.Thread.__init__(self)
        self.project_id = project_id
        self.lib_id = lib_id
        self.dict_id = dict_id
        self.algorithm = algorithm

    def run(self):

        # 获得锁，成功获得锁定后返回True
        # 可选的timeout参数不填时将一直阻塞直到获得锁定
        # 否则超时后将返回False
        threadLock.acquire()
        try:
            self.analysis_event()
        except Exception as e:
            print e
            session = Session()
            project = session.query(AnalysisProject).get(self.project_id)
            project.end_time = datetime.datetime.now()
            project.status = 4  # 4是异常的意思
            session.commit()

        finally:
            # 释放锁
            threadLock.release()


    # 调整petrarch输入内容:调整事件合并开关、输入文本和输入字典
    def init_petrarch(self):

        # 调整合并事件开关
        petr_cn_config = ConfigParser()
        petr_cn_config.read('petrarch_chinese/configFile.ini')
        if self.algorithm == 0:
            petr_cn_config.set('Options', 'merge_event', 'False')
        elif self.algorithm == 1:
            petr_cn_config.set('Options', 'merge_event', 'True')
        try:
            with open('petrarch_chinese/configFile.ini', 'w+') as f:
                petr_cn_config.write(f)
        except Exception as e:
            print (e)

        # 获取输入文本，并写到petrarch对应位置
        lib_tablename = 'rs_textlibrary_data_%s' % self.lib_id
        TextLibraryData.__table__.name = lib_tablename
        session = Session()
        textdata = session.query(TextLibraryData).filter(TextLibraryData.is_delete == 0)
        # textdata = TextLibraryData.query.filter(TextLibraryData.is_delete == 0)

        with io.open('petrarch_chinese/input/test.txt', 'w', encoding='utf-8') as t:
            for data in textdata:
                text_id = data.id
                text_title = data.title if data.title != '' else 'NULL'
                text_summary = data.summary if data.summary != '' else 'NULL'
                text_keywords = data.keywords if data.keywords != '' else 'NULL'
                text_publish_time = data.publish_time if data.publish_time != '' else 'NULL'
                text_author = data.author if data.author != '' else 'NULL'
                text_source = 'NULL'
                text_page = 'NULL'
                text_content = data.content
                text_url = data.url if data.url != '' else 'NULL'
                input_list = [text_id, text_title, text_summary, text_keywords, text_publish_time, text_author,
                              text_source,
                              text_page, text_content, text_url]
                input_list = [str(text) for text in input_list]
                input_text = '|'.join(input_list).decode('utf-8')
                t.write(input_text + '\n')
        session = Session()
        dictionary = session.query(Dictionary).get(self.dict_id)
        dict_name = dictionary.file_name
        petr_config = ConfigParser()
        petr_config.read('petrarch_chinese/petrarch2/data/config/PETR_config.ini')
        petr_config.set('Dictionaries', 'verbfile_name', dict_name)
        petr_config.set('Dictionaries', 'test', 'True')

        with open('petrarch_chinese/petrarch2/data/config/PETR_config.ini', 'w+') as fc:
            petr_config.write(fc)


    # 在子线程中分析文本库的文本，并把提取到的事件载入分析结果库里
    def analysis_event(self):

        # 修改成开始分析状态
        session = Session()
        project = session.query(AnalysisProject).get(self.project_id)
        project.status = 1  # 1是运行中的状态
        session.commit()

        self.init_petrarch()
        art_events = petrarch_chinese_main()

        # 打开对应的结果库
        table_name = 'rs_analysis_event_result_%s' % self.project_id


        # 保存事件
        try:
            for art in art_events:
                events = art_events[art]
                event_num = len(events)
                text_id = art

                event_result = json.dumps(events)
                new_result = AnalycisEventResult(text_id=text_id, event_num=event_num, event_result=event_result)

                insertSQL = "insert into "+table_name+"(text_id,event_num,event_result) values('" + str(text_id) +"','" + str(event_num)+"','"+ event_result+"')"
                # AnalycisEventResultSubThread.__table__.name = table_name
                # temp = AnalycisEventResultSubThread(text_id=text_id,event_num=event_num,event_result=event_result)
                insertSQL = insertSQL.replace(r'"',r'\"')
                insertSQL = insertSQL.replace(r'\u', r'\\u')

                session = Session()
                session.execute(insertSQL)
                session.commit()

            # 修改分析状态
            session = Session()
            project = session.query(AnalysisProject).get(self.project_id)
            project.end_time = datetime.datetime.now()
            project.status = 2  # 2是完成的意思
            session.commit()

            # 将用户事件分析结果保留到指定文件夹

            print("ok")
        except Exception as e:
            session = Session()
            project = session.query(AnalysisProject).get(self.project_id)
            project.end_time = datetime.datetime.now()
            project.status = 4  # 4是异常的意思
            session.commit()
            print ('error')
            print (e)


def test_thread():
    time.sleep(5)
    print("haha")


# 开始一个文本库事件提取
@eventLibApi.route('', methods=['POST'])
def create_analysis_event():
    paras = request.json
    lib_id = paras['lib_id']  # 文本库id
    algorithm = paras['algorithm']  # 分析算法
    type = paras['type']  # 提取分析类型
    name = paras['name']  # 事件提取名称
    dict_id = paras['dic_id']  # 词典id
    uid = g.uid  # 用户id
    # TODO 用户暂时写死，调试用
    if type != 13:
        return jsonify(code=20001, flag=False, message="算法类型错误")

    analysis_project = AnalysisProject(name=name, textlibrary_id=lib_id, analysis_algorithm=algorithm,
                                       analysis_type=type, dictionary_id=dict_id, create_user=uid,
                                       create_time=datetime.datetime.now())
    try:
        db.session.add(analysis_project)
        db.session.commit()
        db.session.flush()
        # 输出新插入数据的主键
        id = analysis_project.id

        # 创建对应的文本库数据表
        create_analysis_result_table(id)

        # 子线程调用petrarch
        analysis_thread = AnalysisThread(id, lib_id, dict_id, algorithm)
        analysis_thread.start()
        return jsonify(code=20000, flag=True, message="创建事件分析结果成功，分析程序将在后台运行")
    except Exception as e:
        print (e)
        return jsonify(code=20001, flag=False, message="创建事件分析结果失败")


# 得到指定位置的分析结果
@eventLibApi.route('/<page>/<size>', methods=['GET'])
def get_analysis_project(page, size):
    try:
        projects = AnalysisProject.query.filter(AnalysisProject.is_delete == 1).all()
        start = (int(page) - 1) * int(size)
        end = min(int(page) * int(size), len(projects))
        result_project = []
        for project in projects[start:end]:
            result_project.append(project.as_dict())
        return jsonify(code=20000, flag=True, message="查询成功", data={"total": len(projects), "rows": result_project})

    except Exception as e:
        print(e)
        return jsonify(code=20001, flag=False, message="查询事件分析结果失败")


# 删除特定的分析工程
@eventLibApi.route('/<id>', methods=['DELETE'])
def delete_analysis_project(id):
    project = AnalysisProject.query.get(id)
    if project is None:
        return jsonify(code=20001, flag=False, message="不存在指定的文本库分析信息")
    db.session.delete(project)

    table_name = 'rs_analysis_event_result_%s' % id
    drop_sql = 'DROP TABLE IF EXISTS {}'.format(table_name)
    db.session.execute(drop_sql)
    db.session.commit()
    return jsonify(code=20000, flag=True, message="删除成功")


# 获得分析状态
@eventLibApi.route('/<id>', methods=['GET'])
def get_analysis_status(id):
    project = AnalysisProject.query.get(id)
    if project is None:
        return jsonify(code=20001, flag=False, message="不存在指定的文本库分析信息")
    status = project.status
    return jsonify(code=20000, flag=True, message="未完成", data={"status": status})


@eventLibApi.route('/detail/<id>', methods=['GET'])
def get_analysis_detail(id):
    project = AnalysisProject.query.get(id)
    if project is None:
        return jsonify(code=20001, flag=False, message="不存在指定的文本库分析信息")
    textlib_id = project.textlibrary_id
    TextLibraryData.__table__.name = 'rs_textlibrary_data_%s' % textlib_id

    result_tablename = 'rs_analysis_event_result_%s' % id
    AnalycisEventResult.__table__.name = result_tablename
    analysis_results = db.session.query(AnalycisEventResult).all()
    results = []
    for analysis_result in analysis_results:
        text_id = analysis_result.text_id
        text_data = TextLibraryData.query.get(text_id)
        result = analysis_result.as_dict()
        result['content'] = text_data.content.encode("utf-8")
        result['title'] = text_data.title
        result['text_id'] = text_id
        unicode_dict_list = json.loads(result['event_result'], encoding='utf-8',strict=False)
        for unicode_dict in unicode_dict_list:
            for key in unicode_dict:
                if key != "origin":
                    unicode_dict[key] = unicode_dict[key].encode("utf-8")
        result['event_result'] = unicode_dict_list
        results.append(result)


    return jsonify(code=20000, flag=True, message="查询成功", data=results)

@eventLibApi.route('/init', methods=['GET'])
def get_libs_and_dicts():
    try:
        libs = TextLibrary.query.filter(TextLibrary.is_delete != 1).all()
        libs_json = []
        for lib in libs:
            libs_json.append(lib.as_dict())
        res = dicModel.Dictionary.query.all()
        data_json = []
        for data in res:
            data_json.append(data.as_dict())
        return jsonify(code=20000, flag=True, message="查询完成", data={"libs": libs_json, "dicts": data_json})
    except:
        return jsonify(code=20001, flag=False, message="查询失败")


@eventLibApi.route('/', methods=['GET'])
def get_events():
    try:
        events = AnalysisProject.query.filter(AnalysisProject.is_delete != 1).all()
        events_json = []
        for event in events:
            events_json.append(event.as_dict())
        return jsonify(code=20000, flag=True, message="查询完成", data={"total": len(events), "json": events_json})
    except:
        return jsonify(code=20001, flag=False, message="查询失败")
