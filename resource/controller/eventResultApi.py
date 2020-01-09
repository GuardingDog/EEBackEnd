# -*- coding: utf-8 -*-

from flask import Flask, blueprints, jsonify, request, Blueprint, g, send_file, make_response, send_from_directory
from resource.model.analysisProjectResultModel import AnalycisEventResult
from resource.model.analysisProjectModel import AnalysisProject
from resource.model.textLibDataModel import TextLibraryData
import json
import xml.dom.minidom
import re
import codecs

eventResultApi = Blueprint(name='event_result', import_name=__name__)


@eventResultApi.route('xml/<articleid>', methods=['GET'])
def get(articleid):
	response = make_response(
		send_from_directory("C:\\Users\\wxn\\Desktop\\1", 'e_result_1' + '.xml', as_attachment=True))
	return response


@eventResultApi.route('/ff/<articleid>/<num>', methods=['GET'])
def event2xml(articleid, num):
	word = []
	fileName = articleid + "-format.txt"

	# fileName = "C:/Users/wxn/Desktop/1/1-format.txt"

	def convertUTF8ToANSI(oldfile, newfile):

		#     打开UTF8文本文件
		f = codecs.open(oldfile, 'r', 'utf8')
		utfstr = f.read()
		f.close()

		# 把UTF8字符串转码成ANSI字符串
		outansestr = utfstr.encode('mbcs')

		# 使用二进制格式保存转码后的文本
		f = open(newfile, 'wb')
		f.write(outansestr)
		f.close()

	oldfile = fileName
	newfile = fileName
	convertUTF8ToANSI(oldfile, newfile)

	with open(fileName, "r") as file:
		char = file.read(0)
		for char in file:
			word.append(char)
	file.close()
	full = str(word[0])

	allContent = full.split()
	index = allContent[0]
	date_all = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", full)
	time_all = re.findall(r"(\d{2}:\d{2}:\d{2})", full)

	index = allContent[0]
	date = date_all[0]
	retime = time_all[0]

	num = 0
	for item in allContent:
		num = num + 1
		if item == retime:
			break
	full = ''
	for j in range(num + 3, len(allContent) - 1):
		full = full + allContent[j]

	def loadDataSet(fileName, splitChar='\t'):

		dataSet = []
		with open(fileName) as fr:
			for line in fr.readlines()[2:]:
				curline = line.strip().split(splitChar)  # 字符串方法strip():返回去除两侧（不包括）内部空格的字符串；字符串方法spilt:按照制定的字符将字符串分割成序列
				fltline = list(map(str, curline))  # list函数将其他类型的序列转换成字符串；map函数将序列curline中的每个元素都转为浮点型
				dataSet.append(fltline)
		return dataSet

	dataSet = loadDataSet(fileName)

	count = 0
	coreData = []

	def detect(text):
		blankLocation = 0
		coreTemp = text
		for qq in coreTemp:
			if qq == ".":
				blankLocation = coreTemp.index(qq)
				break
			elif qq == " ":
				blankLocation = coreTemp.index(qq)
				break

		if blankLocation == 0:
			blankLocation = len(coreTemp)
		return text[0:blankLocation]

	for data in dataSet:
		if ("#e" in str(data)):
			co = count

			event = data[0]
			ids = dataSet[co + 2][1]
			content = dataSet[co + 3][1]
			source = dataSet[co + 4][1]
			target = dataSet[co + 5][1]
			trigger = dataSet[co + 6][1]
			anchor = dataSet[co + 7][1]

			coreData.append(event)
			coreData.append(ids)
			coreData.append(detect(content))
			coreData.append(detect(source))
			coreData.append(target)
			coreData.append(detect(trigger))
			coreData.append(detect(anchor))

		count = count + 1

	# 在内存中创建一个空的文档
	doc = xml.dom.minidom.Document()
	# 创建一个根节点Managers对象
	root = doc.createElement('Body')  # root表示body
	# 设置根节点的属性
	# 将根节点添加到文档对象中
	doc.appendChild(root)

	nodeAge = doc.createElement("content-ID")
	nodeAge.appendChild(doc.createTextNode("Content ID-" + index))
	root.appendChild(nodeAge)

	nodeAge = doc.createElement("fullcontent")
	nodeAge.appendChild(doc.createTextNode(full))
	root.appendChild(nodeAge)

	nodeAge = doc.createElement("reporttime")
	nodeAge.appendChild(doc.createTextNode(date + " " + retime))
	root.appendChild(nodeAge)

	# 记录上一个段落的序号，如果当前这个和上一个的序号不同，则创建新的paragraph
	# 记录上一个句子的序号，如果当前这个和上一个的序号不同，则创建新的sentence
	childParagraphBefore = ""
	childSentenceBefore = ""
	childParagraphNow = ""
	childSentenceNow = ""
	for i in range(len(coreData)):

		if ("#e" in str(coreData[i])):
			ids = coreData[i + 1]
			x = ids.split('_')
			paraNum = x[0]
			sentenceNum = x[1]
			#             x = ids.split('-')
			#             y = x[1].split('_')
			#             aticleNum = x[0]
			#             paraNum = y[0]
			#             sentenceNum = y[1]

			#             sp = '_'
			#             nPos=ids.index(sp)
			childParagraphNow = paraNum
			childSentenceNow = sentenceNum

			if (childParagraphBefore is not childParagraphNow):
				nodeParagraph = doc.createElement('Paragraph')  # 创建段落

				nodeSentence = doc.createElement('Sentence')  # 创建句子

				# 给叶子节点name设置一个文本节点，用于显示文本内容
				nodeParagraph.appendChild(nodeSentence)  # 把句子连在段落上

				nodeEvent = doc.createElement('Event')
				nodeEvent.setAttribute('eid', coreData[i])
				nodeSentence.appendChild(nodeEvent)

				# 位置计算
				content_target = coreData[i + 2]
				content_length = len(content_target)
				content_full = full
				full_length = len(full)
				location = 0
				for j in range(full_length):
					if (content_full[j] == content_target[0]):
						point_j = j
						flag = 0
						point_i = 0
						for k in range(content_length):
							if (content_full[point_j] != content_target[point_i]):
								break
							elif (content_full[point_j] == content_target[point_i]):
								point_j = point_j + 1
								point_i = point_i + 1
								flag = flag + 1
						if (flag == content_length):
							location = j

				content_target = coreData[i + 2]
				content_length = len(content_target)
				location1 = 0
				location2 = 0
				location3 = 0

				# source
				source_target = coreData[i + 3]
				source_target_length = len(source_target)
				for j1 in range(content_length):
					if (content_target[j1] == source_target[0]):
						point_j1 = j1
						flag1 = 0
						point_i1 = 0
						for k1 in range(source_target_length):
							if (content_target[point_j1] != source_target[point_i1]):
								break
							elif (content_target[point_j1] == source_target[point_i1]):
								point_j1 = point_j1 + 1
								point_i1 = point_i1 + 1
								flag1 = flag1 + 1
						if (flag1 == source_target_length):
							location1 = j1

				# trigger
				trigger_target = coreData[i + 5]
				#                 print("191:"+coreData[i + 5])

				trigger_target_length = len(trigger_target)
				for j2 in range(content_length):
					if (content_target[j2] == trigger_target[0]):
						point_j2 = j2
						flag2 = 0
						point_i2 = 0
						for k2 in range(trigger_target_length):
							if (content_target[point_j2] != trigger_target[point_i2]):
								break
							elif (content_target[point_j2] == trigger_target[point_i2]):
								point_j2 = point_j2 + 1
								point_i2 = point_i2 + 1
								flag2 = flag2 + 1
						if (flag2 == trigger_target_length):
							location2 = j2

				# target
				target_target = coreData[i + 4]
				target_target_length = len(target_target)
				for j3 in range(content_length):
					if (content_target[j3] == target_target[0]):
						point_j3 = j3
						flag3 = 0
						point_i3 = 0
						for k3 in range(target_target_length):
							if (content_target[point_j3] != target_target[point_i3]):
								break
							elif (content_target[point_j3] == target_target[point_i3]):
								point_j3 = point_j3 + 1
								point_i3 = point_i3 + 1
								flag3 = flag3 + 1
						if (flag3 == target_target_length):
							location3 = j3

				# 位置计算（end）

				if (coreData[i + 3] in content):
					left1 = 0
					right1 = content.index(coreData[i + 3])
					nodeInvalid = doc.createElement('invalid')
					nodeInvalid.appendChild(doc.createTextNode(content[left1:right1]))  # 存放具体的冗余内容
					nodeEvent.appendChild(nodeInvalid)

				# 检验

				nodeSource = doc.createElement('source')
				nodeSource.setAttribute('begin', str(location + location1))
				nodeSource.setAttribute('end', str(location + location1 + source_target_length - 1))
				# 给叶子节点name设置一个文本节点，用于显示文本内容
				nodeSource.appendChild(doc.createTextNode(coreData[i + 3]))
				nodeEvent.appendChild(nodeSource)

				if (coreData[i + 5] in content):
					print(coreData[i + 3])
					left2 = content.index(coreData[i + 3]) + len(coreData[i + 3])
					right2 = content.index(coreData[i + 5])
					nodeInvalid = doc.createElement('invalid')
					nodeInvalid.appendChild(doc.createTextNode(content[left2:right2]))  # 存放具体的冗余内容
					nodeEvent.appendChild(nodeInvalid)

				nodeTrigger = doc.createElement('trigger')
				nodeTrigger.setAttribute('triggerid', coreData[i + 6][0:3])
				nodeTrigger.setAttribute('begin', str(location + location2))
				nodeTrigger.setAttribute('end', str(location + location2 + trigger_target_length - 1))
				# 给叶子节点name设置一个文本节点，用于显示文本内容
				nodeTrigger.appendChild(doc.createTextNode(coreData[i + 5]))
				nodeEvent.appendChild(nodeTrigger)

				if (coreData[i + 4] in content):
					left3 = content.index(coreData[i + 5]) + len(coreData[i + 5])
					right3 = content.index(coreData[i + 4])
					nodeInvalid = doc.createElement('invalid')
					nodeInvalid.appendChild(doc.createTextNode(content[left3:right3]))  # 存放具体的冗余内容
					nodeEvent.appendChild(nodeInvalid)

				nodeTarget = doc.createElement('target')
				nodeTarget.setAttribute('begin', str(location + location3))
				nodeTarget.setAttribute('end', str(location + location3 + target_target_length - 1))
				# 给叶子节点name设置一个文本节点，用于显示文本内容
				nodeTarget.appendChild(doc.createTextNode(coreData[i + 4]))
				nodeEvent.appendChild(nodeTarget)

				if (coreData[i + 4] in content):
					left3 = content.index(coreData[i + 4]) + len(coreData[i + 4])
					nodeInvalid = doc.createElement('invalid')
					nodeInvalid.appendChild(doc.createTextNode(content[left3:]))  # 存放具体的冗余内容
					nodeEvent.appendChild(nodeInvalid)

				# 将各叶子节点添加到父节点Manager中，
				# 最后将Manager添加到根节点Managers中

				root.appendChild(nodeParagraph)

			elif (childParagraphBefore is childParagraphNow):

				if (childSentenceBefore is not childSentenceNow):

					nodeSentence = doc.createElement('Sentence')  # 创建句子

					# 给叶子节点name设置一个文本节点，用于显示文本内容
					nodeParagraph.appendChild(nodeSentence)  # 把句子0连在段落上

					nodeEvent = doc.createElement('Event')
					nodeEvent.setAttribute('eid', coreData[i])
					nodeSentence.appendChild(nodeEvent)

					# 位置计算
					content_target = coreData[i + 2]
					content_length = len(content_target)
					content_full = full
					full_length = len(full)
					location = 0
					for j in range(full_length):
						if (content_full[j] == content_target[0]):
							point_j = j
							flag = 0
							point_i = 0
							for k in range(content_length):
								if (content_full[point_j] != content_target[point_i]):
									break
								elif (content_full[point_j] == content_target[point_i]):
									point_j = point_j + 1
									point_i = point_i + 1
									flag = flag + 1
							if (flag == content_length):
								location = j

					content_target = coreData[i + 2]
					content_length = len(content_target)
					location1 = 0
					location2 = 0
					location3 = 0

					# source
					source_target = coreData[i + 3]
					source_target_length = len(source_target)
					for j1 in range(content_length):
						if (content_target[j1] == source_target[0]):
							point_j1 = j1
							flag1 = 0
							point_i1 = 0
							for k1 in range(source_target_length):
								if (content_target[point_j1] != source_target[point_i1]):
									break
								elif (content_target[point_j1] == source_target[point_i1]):
									point_j1 = point_j1 + 1
									point_i1 = point_i1 + 1
									flag1 = flag1 + 1
							if (flag1 == source_target_length):
								location1 = j1

					# trigger
					trigger_target = coreData[i + 5]
					trigger_target_length = len(trigger_target)
					for j2 in range(content_length):
						if (content_target[j2] == trigger_target[0]):
							point_j2 = j2
							flag2 = 0
							point_i2 = 0
							for k2 in range(trigger_target_length):
								if (content_target[point_j2] != trigger_target[point_i2]):
									break
								elif (content_target[point_j2] == trigger_target[point_i2]):
									point_j2 = point_j2 + 1
									point_i2 = point_i2 + 1
									flag2 = flag2 + 1
							if (flag2 == trigger_target_length):
								location2 = j2

					# target
					target_target = coreData[i + 4]
					target_target_length = len(target_target)
					for j3 in range(content_length):
						if (content_target[j3] == target_target[0]):
							point_j3 = j3
							flag3 = 0
							point_i3 = 0
							for k3 in range(target_target_length):
								if (content_target[point_j3] != target_target[point_i3]):
									break
								elif (content_target[point_j3] == target_target[point_i3]):
									point_j3 = point_j3 + 1
									point_i3 = point_i3 + 1
									flag3 = flag3 + 1
							if (flag3 == target_target_length):
								location3 = j3

					if (coreData[i + 3] in content):
						left1 = 0
						right1 = content.index(coreData[i + 3])
						nodeInvalid = doc.createElement('invalid')
						nodeInvalid.appendChild(doc.createTextNode(content[left1:right1]))  # 存放具体的冗余内容
						nodeEvent.appendChild(nodeInvalid)

					nodeSource = doc.createElement('source')
					nodeSource.setAttribute('begin', str(location + location1))
					nodeSource.setAttribute('end', str(location + location1 + source_target_length - 1))
					# 给叶子节点name设置一个文本节点，用于显示文本内容
					nodeSource.appendChild(doc.createTextNode(coreData[i + 3]))
					nodeEvent.appendChild(nodeSource)

					if (coreData[i + 5] in content):
						left2 = content.index(coreData[i + 3]) + len(coreData[i + 3])
						right2 = content.index(coreData[i + 5])
						nodeInvalid = doc.createElement('invalid')
						nodeInvalid.appendChild(doc.createTextNode(content[left2:right2]))  # 存放具体的冗余内容
						nodeEvent.appendChild(nodeInvalid)

					nodeTrigger = doc.createElement('trigger')
					nodeTrigger.setAttribute('triggerid', coreData[i + 6][0:3])
					nodeTrigger.setAttribute('begin', str(location + location2))
					nodeTrigger.setAttribute('end', str(location + location2 + trigger_target_length - 1))
					# 给叶子节点name设置一个文本节点，用于显示文本内容
					nodeTrigger.appendChild(doc.createTextNode(coreData[i + 5]))
					nodeEvent.appendChild(nodeTrigger)

					if (coreData[i + 4] in content):
						left3 = content.index(coreData[i + 5]) + len(coreData[i + 5])
						right3 = content.index(coreData[i + 4])
						nodeInvalid = doc.createElement('invalid')
						nodeInvalid.appendChild(doc.createTextNode(content[left3:right3]))  # 存放具体的冗余内容
						nodeEvent.appendChild(nodeInvalid)

					nodeTarget = doc.createElement('target')
					nodeTarget.setAttribute('begin', str(location + location3))
					nodeTarget.setAttribute('end', str(location + location3 + target_target_length - 1))
					# 给叶子节点name设置一个文本节点，用于显示文本内容
					nodeTarget.appendChild(doc.createTextNode(coreData[i + 4]))
					nodeEvent.appendChild(nodeTarget)

					if (coreData[i + 4] in content):
						left3 = content.index(coreData[i + 4]) + len(coreData[i + 4])
						nodeInvalid = doc.createElement('invalid')
						nodeInvalid.appendChild(doc.createTextNode(content[left3:]))  # 存放具体的冗余内容
						nodeEvent.appendChild(nodeInvalid)


				elif (childSentenceBefore is childSentenceNow):

					nodeEvent = doc.createElement('Event')
					nodeEvent.setAttribute('eid', coreData[i])
					nodeSentence.appendChild(nodeEvent)

					# 位置计算
					content_target = coreData[i + 2]
					content_length = len(content_target)
					content_full = full
					full_length = len(full)
					location = 0
					for j in range(full_length):
						if (content_full[j] == content_target[0]):
							point_j = j
							flag = 0
							point_i = 0
							for k in range(content_length):
								if (content_full[point_j] != content_target[point_i]):
									break
								elif (content_full[point_j] == content_target[point_i]):
									point_j = point_j + 1
									point_i = point_i + 1
									flag = flag + 1
							if (flag == content_length):
								location = j

					content_target = coreData[i + 2]
					content_length = len(content_target)
					location1 = 0
					location2 = 0
					location3 = 0

					# source
					source_target = coreData[i + 3]
					source_target_length = len(source_target)
					for j1 in range(content_length):
						if (content_target[j1] == source_target[0]):
							point_j1 = j1
							flag1 = 0
							point_i1 = 0
							for k1 in range(source_target_length):
								if (content_target[point_j1] != source_target[point_i1]):
									break
								elif (content_target[point_j1] == source_target[point_i1]):
									point_j1 = point_j1 + 1
									point_i1 = point_i1 + 1
									flag1 = flag1 + 1
							if (flag1 == source_target_length):
								location1 = j1

					trigger_target = coreData[i + 5]
					trigger_target_length = len(trigger_target)
					for j2 in range(content_length):
						if (content_target[j2] == trigger_target[0]):
							point_j2 = j2
							flag2 = 0
							point_i2 = 0
							for k2 in range(trigger_target_length):
								if (content_target[point_j2] != trigger_target[point_i2]):
									break
								elif (content_target[point_j2] == trigger_target[point_i2]):
									point_j2 = point_j2 + 1
									point_i2 = point_i2 + 1
									flag2 = flag2 + 1
							if (flag2 == trigger_target_length):
								location2 = j2

					# target
					target_target = coreData[i + 4]
					target_target_length = len(target_target)
					for j3 in range(content_length):
						if (content_target[j3] == target_target[0]):
							point_j3 = j3
							flag3 = 0
							point_i3 = 0
							for k3 in range(target_target_length):
								if (content_target[point_j3] != target_target[point_i3]):
									break
								elif (content_target[point_j3] == target_target[point_i3]):
									point_j3 = point_j3 + 1
									point_i3 = point_i3 + 1
									flag3 = flag3 + 1
							if (flag3 == target_target_length):
								location3 = j3

					if (coreData[i + 3] in content):
						left1 = 0
						right1 = content.index(coreData[i + 3])

						nodeInvalid = doc.createElement('invalid')
						nodeInvalid.appendChild(doc.createTextNode(content[left1:right1]))  # 存放具体的冗余内容
						nodeEvent.appendChild(nodeInvalid)

					nodeSource = doc.createElement('source')
					nodeSource.setAttribute('begin', str(location + location1))
					nodeSource.setAttribute('end', str(location + location1 + source_target_length - 1))
					# 给叶子节点name设置一个文本节点，用于显示文本内容
					nodeSource.appendChild(doc.createTextNode(coreData[i + 3]))
					nodeEvent.appendChild(nodeSource)

					if (coreData[i + 5] in content):
						left2 = content.index(coreData[i + 3]) + len(coreData[i + 3])
						right2 = content.index(coreData[i + 5])
						nodeInvalid = doc.createElement('invalid')
						nodeInvalid.appendChild(doc.createTextNode(content[left2:right2]))  # 存放具体的冗余内容
						nodeEvent.appendChild(nodeInvalid)

					nodeTrigger = doc.createElement('trigger')
					nodeTrigger.setAttribute('triggerid', coreData[i + 6][0:3])
					nodeTrigger.setAttribute('begin', str(location + location2))
					nodeTrigger.setAttribute('end', str(location + location2 + trigger_target_length - 1))
					# 给叶子节点name设置一个文本节点，用于显示文本内容
					nodeTrigger.appendChild(doc.createTextNode(coreData[i + 5]))
					nodeEvent.appendChild(nodeTrigger)

					if (coreData[i + 4] in content):
						left3 = content.index(coreData[i + 5]) + len(coreData[i + 5])
						right3 = content.index(coreData[i + 4])
						nodeInvalid = doc.createElement('invalid')
						nodeInvalid.appendChild(doc.createTextNode(content[left3:right3]))  # 存放具体的冗余内容
						nodeEvent.appendChild(nodeInvalid)

					nodeTarget = doc.createElement('target')
					nodeTarget.setAttribute('begin', str(location + location3))
					nodeTarget.setAttribute('end', str(location + location3 + target_target_length - 1))
					# 给叶子节点name设置一个文本节点，用于显示文本内容
					nodeTarget.appendChild(doc.createTextNode(coreData[i + 4]))
					nodeEvent.appendChild(nodeTarget)

					if (coreData[i + 4] in content):
						left3 = content.index(coreData[i + 4]) + len(coreData[i + 4])
						nodeInvalid = doc.createElement('invalid')
						nodeInvalid.appendChild(doc.createTextNode(content[left3:]))  # 存放具体的冗余内容
						nodeEvent.appendChild(nodeInvalid)

		childParagraphBefore = childParagraphNow
		childSentenceBefore = childSentenceNow

	# 开始写xml文档
	#     i = 1
	fp = open('C:\\Users\\wxn\\Desktop\\1\\e_result_' + index + '.xml', 'w')
	doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="gbk")
	# response = make_response(
	# 	send_from_directory("C:\\Users\\wxn\\Desktop\\1", 'e_result_' + index + '.xml', as_attachment=True))
	return "dahsi"

@eventResultApi.route('/<id>', methods=['GET'])
def get_event_result(id):
	try:
		table_name = 'rs_analysis_project_' + id
		AnalycisEventResult.__table__.name = table_name
		results = AnalycisEventResult.query.filter(AnalycisEventResult.text_id == id).all()
		result_data = []
		for result in results:
			result_data.append(result.as_dct())
		return jsonify(code=20000, flag=True, message="查询成功", data={"total": len(result_data), "rows": result_data})
	except Exception as e:
		print(e)
		return jsonify(code=20001, flag=False, message="查询分析结果失败")


@eventResultApi.route('/detail/<project_id>/<text_id>', methods=['GET'])
def get_event_detail(project_id, text_id):
	project = AnalysisProject.query.get(project_id)

	# 查询content
	textlib_id = project.textlibrary_id
	textlibrary_data_tablename = 'rs_textlibrary_data_%s' % textlib_id
	TextLibraryData.__table__.name = textlibrary_data_tablename
	text_data = TextLibraryData.query.get(text_id)
	text_dict = text_data.as_dict()
	paragraphs = text_data.content.decode("utf-8").split(u"\u3000")
	# remove the empty str
	paragraphs = filter(None, paragraphs)
	res = []
	for p in paragraphs:
		p = '\t' + p
		res.append(p)
	text_dict.update({"content": res})

	# 查询result
	result_tablename = 'rs_analysis_event_result_%s' % project_id
	AnalycisEventResult.__table__.name = result_tablename
	result = AnalycisEventResult.query.filter(AnalycisEventResult.text_id == text_id).all()
	result = result[0].as_dict()['event_result']
	result = json.loads(result, encoding='utf-8',strict=False)

	results = []

	for i_result in result:
		origin = i_result["origin"].split(" ")
		content = i_result["content"].encode("utf-8")
		# get Source
		source = origin[2]
		if "source" in i_result and i_result["source"] != '---':
			source = i_result["source"]
		target = origin[3]
		if "target" in i_result and i_result["target"] != '---':
			target = i_result["target"]
		if "eventroot" in i_result and i_result["eventroot"] != '---':
			ls = i_result["eventroot"].split(" ")
			if len(ls) > 1:
				event_code = i_result["eventroot"].split(" ")[1]
			else:
				event_code = i_result["eventroot"].split(" ")[0]
		else:
			event_code = origin[4]
		event_code += " "
		if "eventtext" in i_result:
			event_code += i_result["eventtext"]
		else:
			event_code += "---"
		results.append({"source": source, "target": target, "event": event_code, "location": i_result["location"],
						"rs": source+" " + event_code + " " + target, "content": content,"sentenceTime": i_result["sentenceTime"]})

	return jsonify(code=20000, flag=True, message="查询成功", text=text_dict, events=results)

