#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
from time import sleep
from datetime import datetime, timedelta
import vk_auth

def get_json(url):
	getjson = urllib.request.urlopen(url).readall().decode('utf-8')
	getjson = json.loads(getjson)
	sleep(0.3)
	return getjson

app_id = '5397060'
access_token = vk_auth.auth('vktool@mail.ru', 'vkpassvk', app_id, 'offline')[0]
#access_token = 'ab73388da5be5f3b7966188d10471c031d6ff78c7b54ee92293d4f102d02f09808b6a40d46d4b87ee52f4'

print (access_token)

publics_list = open('../config/config.json').read()
publics_list = json.loads(publics_list)

title = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"', ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', ' xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd"', ' xmlns:y="http://www.yworks.com/xml/graphml"', ' xmlns:yed="http://www.yworks.com/xml/yed/3">', '  <key for="node" id="d1" yfiles.type="nodegraphics"/>', '  <graph edgedefault="directed" id="G">']
graph_people = open("../results/graphml/friends_graph.graphml", 'w')
graph_groups = open("../results/graphml/groups_graph.graphml", 'w')
for line in title:
        graph_people.write(line+'\n')
        graph_groups.write(line+'\n')

users=[]
for i in range (len(publics_list['public_id'])):
	offset = 0;
	url = 'https://api.vk.com/method/groups.getMembers?fields=name&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_id'][i])
	members = get_json(url)
	try:
		members = get_json(url)
	except:
		print ('failed')
	members_count = members['response']['count']
	while True:
		url = 'https://api.vk.com/method/groups.getMembers?fields=name,sex,bdate,city,universities&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_id'][i])
		try:
			members = get_json(url)
		except:
			print ('failed')
		if 'response' in members:
			for member in members['response']['users']:
				if not (member['uid'] in users):
					users.append(member['uid'])
					print ('info ' + str(member['uid']))

					graph_people.write('    <node id="' + str(member['uid']) + '">'+'\n')
					graph_people.write('      <data key="d1">'+'\n')
					graph_people.write('        <y:ShapeNode>'+'\n')
					graph_people.write('          <y:NodeLabel>' + member['first_name'] + ' ' + member['last_name'] + '</y:NodeLabel> '+'\n')
					graph_people.write('        </y:ShapeNode>'+'\n')
					graph_people.write('      </data>'+'\n')
					graph_people.write('    </node>'+'\n')

					graph_groups.write('    <node id="' + str(member['uid']) + '">'+'\n')
					graph_groups.write('      <data key="d1">'+'\n')
					graph_groups.write('        <y:ShapeNode>'+'\n')
					graph_groups.write('          <y:NodeLabel>' + member['first_name'] + ' ' + member['last_name'] + '</y:NodeLabel> '+'\n')
					graph_groups.write('        </y:ShapeNode>'+'\n')
					graph_groups.write('      </data>'+'\n')
					graph_groups.write('    </node>'+'\n')

		if (offset + 1000 > members_count):
			break
		offset += 1000

edge_num = 0
group_list = []
for user in users:
        print (user)
        friends_url = 'https://api.vk.com/method/friends.get?access_token=' + access_token + '&fields=name&user_id=' + str(user)
        try:
                friends = get_json(friends_url)
        except:
                print ('failed')
        if ('response' in friends):
                for friend in friends['response']:
                        if (friend['uid'] > user):
                                if (friend['uid'] in users):
                                        graph_people.write('<edge id="e' + str(edge_num) + '" source="' + str(user) + '" target="' + str(friend['uid']) + '"/>' + '\n')
                                        edge_num += 1

        group_url = 'https://api.vk.com/method/groups.get?access_token=' + access_token + '&extended=1&count=1000&user_id=' + str(user)
        try:
                groups = get_json(group_url)
        except:
                print ('failed')
        if ('response' in groups):
                del groups['response'][0]
                for group in groups['response']:
                        if (group['gid'] not in group_list):
                                group_list.append(group['gid'])
                                graph_groups.write('    <node id="' + str(group['gid']) + '">'+'\n')
                                graph_groups.write('      <data key="d1">'+'\n')
                                graph_groups.write('        <y:ShapeNode>'+'\n')
                                graph_groups.write('          <y:NodeLabel>' + str(group['name']) + '</y:NodeLabel> '+'\n')
                                graph_groups.write('        </y:ShapeNode>'+'\n')
                                graph_groups.write('      </data>'+'\n')
                                graph_groups.write('    </node>'+'\n')

                        graph_groups.write('    <edge id="e' + str(edge_num) + '" source="' + str(user) + '" target="' + str(group['gid']) + '"/>' + '\n')
                        edge_num += 1

graph_people.write('  </graph>' + '\n')
graph_people.write('</graphml>' + '\n')

graph_groups.write('  </graph>' + '\n')
graph_groups.write('</graphml>' + '\n')
