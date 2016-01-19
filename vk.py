import urllib2
import json
from time import sleep
import vk_auth

app_id = '4990791'
access_token = vk_auth.auth('vktool@mail.ru', 'vkpassvk', app_id, 'offline,messages')[0]

publics_list = open('publics.json').read()
publics_list = json.loads(publics_list)

title = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"', ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', ' xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd"', ' xmlns:y="http://www.yworks.com/xml/graphml"', ' xmlns:yed="http://www.yworks.com/xml/yed/3">', '  <key for="node" id="d1" yfiles.type="nodegraphics"/>', '  <graph edgedefault="directed" id="G">']
graph = open("graph.graphml", 'w')
for line in title:
	print >>graph, line

users=[]
for i in range (len(publics_list['public_ids'])):
	offset = 0;
	url = 'https://api.vk.com/method/groups.getMembers?fields=name&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_ids'][i])
	members = urllib2.urlopen(url).read()
	members = json.loads(members)
	members_count = members['response']['count']
	while True:
		url = 'https://api.vk.com/method/groups.getMembers?fields=name&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_ids'][i])
		members = urllib2.urlopen(url).read()
		members = json.loads(members)
		for member in members['response']['users']:
			if not (member['uid'] in users):
				users.append(member['uid'])
				print >>graph, '    <node id="' + str(member['uid']) + '">'
				print >>graph, '      <data key="d1">'
				print >>graph, '        <y:ShapeNode>'
				print >>graph, '          <y:NodeLabel>' + member['first_name'].encode("utf-8") + ' ' + member['last_name'].encode("utf-8") + '</y:NodeLabel> '
				print >>graph, '        </y:ShapeNode>'
				print >>graph, '      </data>'
				print >>graph, '    </node>'
		if (offset + 1000 > members_count):
			break
		offset += 1000

edge_num = 0
for user in users:
	print user
	friends_url = 'https://api.vk.com/method/friends.get?access_token=' + access_token + '&fields=name&user_id=' + str(user)
	friends = urllib2.urlopen(friends_url).read()
	friends = json.loads(friends)
	if ('response' in friends):
		for friend in friends['response']:
			if (friend['uid'] > user):
				if (friend['uid'] in users):
					print >>graph, '<edge id="e' + str(edge_num) + '" source="' + str(user) + '" target="' + str(friend['uid']) + '"/>'
					edge_num += 1
print >>graph, '  </graph>'
print >>graph, '</graphml>'