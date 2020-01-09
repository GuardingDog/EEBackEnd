# -*- coding: utf-8 -*-

from resource import db

class TextLibraryData(db.Model):
    """文本库数据表"""
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255))
    summary = db.Column(db.Text)
    keywords = db.Column(db.String(255))
    publish_time = db.Column(db.DateTime)
    author = db.Column(db.String(255))
    content = db.Column(db.Text)
    url = db.Column(db.String(512))
    create_time = db.Column(db.DateTime)
    # 0表示未删除
    is_delete = db.Column(db.Integer, default=0)

    def as_dict(self):
        o_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if o_dict['create_time']:
            o_dict['create_time'] = o_dict['create_time'].strftime(u'%Y-%m-%d %H:%m:%S')
        if o_dict['publish_time']:
            o_dict['publish_time'] = o_dict['publish_time'].strftime(u'%Y-%m-%d %H:%m:%S')
        return o_dict

    def __repr__(self):
        return '<TEXT_LIBRARY_DATA {}>'.format(self.title)
