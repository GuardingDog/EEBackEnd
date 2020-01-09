# -*- coding: utf-8 -*-

from resource import db

class AnalysisProject(db.Model):
	"""文本库分析表"""
	__tablename__ = 'rs_analysis_project'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	analysis_fields = db.Column(db.String(255))
	analysis_algorithm = db.Column(db.Integer)
	analysis_type = db.Column(db.Integer)
	status = db.Column(db.Integer, default=0) # 0为未完成， 1为已完成
	dictionary_id = db.Column(db.Integer)
	textlibrary_id = db.Column(db.Integer)
	create_time = db.Column(db.DateTime)
	create_user = db.Column(db.Integer)
	start_time = db.Column(db.DateTime)
	end_time = db.Column(db.DateTime)

	is_delete = db.Column(db.Integer, default=0)
	delete_user = db.Column(db.Integer)

	def as_dict(self):
		o_dict = {c.name: getattr(self, c.name) for c in self.__table__.columns}
		if o_dict['create_time']:
			o_dict['create_time'] = o_dict['create_time'].strftime(u'%Y-%m-%d %H:%m:%S')
		if o_dict['start_time']:
			o_dict['start_time'] = o_dict['start_time'].strftime(u'%Y-%m-%d %H:%m:%S')
		if o_dict['end_time']:
			o_dict['end_time'] = o_dict['end_time'].strftime(u'%Y-%m-%d %H:%m:%S')
		return o_dict

	def __repr__(self):
		return '<Analysis Project {}>'.format(self.name)
