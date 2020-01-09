# -*- coding: utf-8 -*-

# import mysql.connector
#
#
# def get_db():
# 	mydb = mysql.connector.connect(
# 		host="118.25.153.97",
# 		user="root",
# 		passwd="123456",
# 		database="SoftwareEngineering"
# 	)
#
# 	return mydb
#
#
# def create_textlib_date(textlib_id):
# 	table_name = 'rs_textlibrary_data_%s' % textlib_id
# 	drop_sql = 'DROP TABLE IF EXISTS {};'.format(table_name)
# 	create_sql = 'CREATE TABLE IF NOT EXISTS {}(' \
# 		  'id int(11) not null primary key,' \
# 		  'title varchar(255),' \
# 		  'summary text,' \
# 		  'keywords varchar(255),' \
# 		  'publish_time datetime,' \
# 		  'author varchar(255),' \
# 		  'source varchar(255),' \
# 		  'page varchar(20),' \
# 		  'content text,' \
# 		  'url varchar(512),' \
# 		  'publish_source varchar(255),' \
# 		  'create_time datetime,' \
# 		  'is_delete int(11)' \
# 		  ');'.format(table_name)
#
# 	mydb = get_db()
# 	cursor = mydb.cursor()
# 	cursor.execute(drop_sql)
# 	cursor.execute(create_sql)
# 	mydb.commit()
#
# 	db_sql = 'show databases'
# 	cursor.execute(db_sql)
# 	print(cursor.fetchall())
# 	mydb.disconnect()
#
# def create_analysis_result(project_id):
# 	table_name = 'rs_analysis_event_result_%s' % project_id
# 	drop_sql = 'DROP TABLE IF EXISTS {}'.format(table_name)
# 	create_sql = 'create table IF NOT EXISTS {}(' \
# 				 'id int(20) not null primary key,'\
# 				 'text_id varchar(255) not null,'\
# 				 'recall_rate decimal(10,2) not null,'\
# 				 'accuracy_rate decimal(10,2) not null,'\
# 				 'event_num int(11) not null,'\
# 				 'event_result text not null'\
# 				 ')'.format(table_name)

#
# def test():
# 	# 动态生成两个类型的表，没有返回任何信息
# 	create_textlib_date('1')
# 	# create_analysis_result('1')
#
# 	# 外边调用执行任意sql语句
# 	mydb = get_db()
# 	cursor = mydb.cursor()
#
# 	sql = "INSERT INTO `SoftwareEngineering`.`test` (`id`, `testcol`) VALUES (%s, %s);"
# 	# sql = "SELECT * FROM SoftwareEngineering.test;"
# 	val = ("4", "444")
# 	# cursor.execute(sql, val)
# 	db_sql = "SHOW DATABASES"
# 	cursor.execute(db_sql)
# 	result = cursor.fetchone()
# 	# mydb.commit()
# 	print(result)
# 	mydb.disconnect()
#
# if __name__ == '__main__':
# 	test()
