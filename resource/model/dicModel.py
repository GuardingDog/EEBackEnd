# -*- coding: utf-8 -*-
from resource import db


class Dictionary(db.Model):
    """词典表"""
    __tablename__ = "rs_analysis_event_library"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255))
    file_name=db.Column(db.String(255))
    create_user = db.Column(db.Integer)
    create_time = db.Column(db.DateTime)

    def as_dict(self):
        o_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if o_dict['create_time']:
            o_dict['create_time'] = o_dict['create_time'].strftime(u'%Y-%m-%d %H:%m:%S')
        return o_dict

    def __repr__(self):
        return '<Dictionary {}>'.format(self.name)
