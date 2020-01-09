# import

把所有引用到gcp的模块import方式都加上from . / from ..



# 返回事件

## main.py

1. 修改函数名字main() 成 petrarch_chinese_main()

2. 在petrarch_chinese_main()最后一行加上返回语句

   ```
   return petrarch2_main(args)
   ```

## petrarch2.py

1. 修改import路径

   ```
   from ..timeRecognition.TimeNormalizer import TimeNormalizer
   ```

2. main方法里新加返回值

   ```python
   if cli_args.command_name == 'parse':
   	events = run(paths, out, cli_args.parsed)
   else:    
       events = run(paths, out, True)  # <===
   print("Coding time:", time.time() - start_time)
   print("Finished")
   return events
   ```

3. run方法新加返回值

   ```python
   updated_events =do_coding(events)
   print("update_event:")
   #print(json.dumps(updated_events, ensure_ascii=False, encoding='utf-8'))
   if PETRglobals.NullVerbs:    
       output_event = PETRwriter.write_nullverbs(updated_events, 'nullverbs.' + out_file)
   elif PETRglobals.NullActors:    
   	output_event = PETRwriter.write_nullactors(updated_events, 'nullactors.txt')
   else:
       output_event = PETRwriter.write_events(updated_events, out_file)
   return output_event
   ```

## PETRwriter.py

1. write_event方法

   新增局部变量all_events_outer_dict={}用于返回

2. write_event方法 向all_events_outer_dict添加内容

   ```python
   event_str, events_list = get_event_str(event_temp, event_dict)
   if events_list is not None:    
   	if article_id not in all_events_outer_dict.keys():
           all_events_outer_dict[article_id] = events_list    
       else:        
           all_events_outer_dict[article_id] = all_events_outer_dict[article_id] + events_list
   ```

3. write_event get_event_str() 一项一项向all_events_outer_dict()添加内容

   ```python
   def get_event_str(events_dict, event_dict):
   	global StorySource
   	global NEvents
   	global StoryIssues
   	global StoryNer
   	global StoryNer2
   
   	strs = []
   	events_outer_list = []
   
   	for event in events_dict:
   
   		# 不输出不完整事件
   		if check_miss_component(event["origin"]) != 3:
   			continue
   		# 输出事件
   		event_outer_dict = {}
   
   		article_id = event['ids'][0].split("-")[0]
   		event_outer_dict.update({"id": article_id})
   
   		ids = ';'.join(event['ids'])
   		contents = []
   		for id in event['ids']:
   			contents.append(get_content_from_id(id, event_dict))
   		contents_str = ";".join(contents)
   
   		# 15.04.30: a very crude hack around an error involving multi-word
   		# verbs
   		if not isinstance(event["origin"][3], basestring):
   			event_str = '\t'.join(
   				event["origin"][:3]) + '\t010\t' + '\t'.join(event["origin"][4:])
   		else:
   			event_str = '\t'.join(event["origin"])
   			event_outer_dict.update({"origin": ' '.join(event["origin"])})
   
   		if "joined_issues" in event:
   			event_str += '\n\tjoined_issues\t{}\n'.format(event["joined_issues"])
   		else:
   			event_str += '\n\tjoined_issues\tnull\n'
   
   		if "url" in event:
   			event_str += '\tids\t{}\n\turl\t{}\n\tStorySource\t{}\n'.format(ids, event["url"], StorySource)
   		else:
   			event_str += '\tids\t{}\n\tStorySource\t{}\n'.format(ids, StorySource)
   
   		if PETRglobals.WriteContent:
   			if 'content' in event:
   				event_str += '\tcontent\t{}\n'.format(
   					contents_str)
   				event_outer_dict.update({"content": contents_str})
   			else:
   				event_str += '\tcontent\t---\n'
   				event_outer_dict.update({"content": '---'})
   
   		if PETRglobals.WriteSource:
   			if 'Source' in event:
   				event_str += '\tSource\t{}\n'.format(
   					event['Source'])
   				event_outer_dict.update({"source": event["Source"]})
   			else:
   				event_str += '\tSource\t---\n'
   				event_outer_dict.update({"source": "---"})
   
   		if PETRglobals.WriteTarget:
   			if 'Target' in event:
   				event_str += '\tTarget\t{}\n'.format(
   					event['Target'])
   				event_outer_dict.update({"target": event["Target"]})
   			else:
   				event_str += '\tTarget\t---\n'
   				event_outer_dict.update({"target": '---'})
   
   		if PETRglobals.WriteActorText:
   			if 'actortext' in event:
   				event_str += '\tactortext\t{}\t{}\n'.format(
   					event['actortext'][0],
   					event['actortext'][1])
   				event_outer_dict.update({"actortext": event["actortext"][0] + '\t' + event['actortext'][1]})
   			else:
   				event_str += '\tactortext\t---\t---\n'
   				event_outer_dict.update({"actortext": '---' + '\t' + '---'})
   
   		if PETRglobals.WriteEventText:
   			if 'eventtext' in event:
   				event_str += '\teventtext\t{}\n'.format(
   					event['eventtext'])
   				event_outer_dict.update({"eventtext": event["eventtext"]})
   			else:
   				event_str += '\teventtext\t---\n'
   				event_outer_dict.update({"eventtext": '---'})
   		# if True:
   		if PETRglobals.WriteActorRoot:
   			if 'actorroot' in event:
   				event_str += '\tactorroot\t{}\t{}\n'.format(
   					event['actorroot'][0],
   					event['actorroot'][1])
   				event_outer_dict.update({"actorroot": event["actorroot"][0] + '\t' + event["actorroot"][1]})
   			else:
   				event_str += '\tactorroot\t---\t---\n'
   				event_outer_dict.update({"actorroot": '---' + '\t' + '---'})
   
   		if PETRglobals.WriteEventRoot:
   			if 'eventroot' in event:
   				event_str += '\teventroot\t{}\n'.format(
   					event['eventroot'])
   				event_outer_dict.update({"eventroot": event['eventroot']})
   			else:
   				event_str += '\teventroot\t---\n'
   				event_outer_dict.update({"eventroot": '---'})
   
   		if PETRglobals.WriteNer:
   			event_str += '\tlocation1\t{}\n'.format(StoryNer)
   			if (StoryNer2):
   				location2_str = ",".join(StoryNer2)
   			else:
   				location2_str = "未提取出地点"
   			event_str += '\tlocation2\t{}\n'.format(location2_str)
   			event_outer_dict.update({"location": location2_str})
   		events_outer_list.append(event_outer_dict)
   		strs.append(event_str)
   	if len(strs) == 0:
   		return None, None
   	return strs, events_outer_list
   ```

# 修改verb字典

1. 在petrarch2 utilities.py 434行_get_data()函数下方添加一个类似的函数

   ```python
   def _get_dict_data(dir_path, path):
   	cwd = sys.path[0]
   	joined = os.path.join(dir_path, path)
   	out_dir = os.path.join(cwd, joined)
   	return out_dir
   ```

   2. petrarch2.py read_dictionaries()中
       818行动词路径这个变量赋值方式更改一下

     ```python
     verb_path = utilities._get_dict_data(
             'dictionary',
             PETRglobals.VerbFileName
         )
     ```

   3. 在PETRreader.py read_verb_dictionary(verb_path)开始添加刷新字典 
   
      ```python
      PETRglobals.VerbDict = {'phrases': {}, 'verbs': {}, 'transformation': {}}
      ```

# 修改配置文件

大概是在所有path前添加一层

```ini
[Options]
input_path = petrarch_chinese/input/
input_name = test.txt
xml_output_path = petrarch_chinese/output/
xml_output_name = test123.xml
xml_file_name = format_text
output_path = petrarch_chinese/
output_name = evts.result.txt
format_text = multiformat_text
neg_dic_path = petrarch_chinese/petrarch2/data/dictionaries/MyNegDic.txt
prep_dic_path = petrarch_chinese/petrarch2/data/dictionaries/MyPrepDic.txt
port = -1
merge_event = True
output_zero_flag = 1
getnullactor = False

[StanfordNLP]
stanford_dir = stanford-corenlp-full-2018-10-05
corenlp_parse = False


```

