# -*- coding: utf-8 -*-

from resource import db


class AnalycisEventResult(db.Model):
	# 事件分类结果
	id = db.Column(db.Integer, primary_key=True)
	text_id = db.Column(db.String(255))
	recall_rate = db.Column(db.DECIMAL)
	accuracy_rate = db.Column(db.DECIMAL)
	event_num = db.Column(db.Integer)
	event_result = db.Column(db.Text)

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

	def __repr__(self):
		return '<Analysis_Event_Result {}>'.format(self.id)
