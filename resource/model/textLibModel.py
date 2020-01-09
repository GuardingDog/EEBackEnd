# -*- coding: utf-8 -*-

from resource import db


class TextLibrary(db.Model):
    """文本库表"""
    __tablename__ = "rs_textlibrary"
    id = db.Column(db.Integer,primary_key=True)
    textlibrary_name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    line_no = db.Column(db.Integer, default=0)
    # 0表示未导入
    import_status = db.Column(db.Integer, default=0)
    create_user = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)
    # 0表示未删除
    is_delete = db.Column(db.Integer, default=0)
    delete_time = db.Column(db.DateTime)

    def as_dict(self):
        o_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if o_dict['create_time']:
            o_dict['create_time'] = o_dict['create_time'].strftime(u'%Y-%m-%d %H:%m:%S')
        if o_dict['delete_time']:
            o_dict['delete_time'] = o_dict['delete_time'].strftime(u'%Y-%m-%d %H:%m:%S')
        return o_dict

    def __repr__(self):
        return '<TEXT_LIBRARY {}>'.format(self.textlibrary_name)
