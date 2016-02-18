import urllib2
import json
from time import sleep
from datetime import datetime, timedelta
import vk_auth

app_id = '4990791'
access_token = vk_auth.auth('vktool@mail.ru', 'vkpassvk', app_id, 'offline,messages')[0]
print access_token

publics_list = open('publics.json').read()
publics_list = json.loads(publics_list)

sex = ['F', 'M']

title = ['<?xml version="1.0" encoding="UTF-8" standalone="no"?>', '<graphml xmlns="http://graphml.graphdrawing.org/xmlns"', ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', ' xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd"', ' xmlns:y="http://www.yworks.com/xml/graphml"', ' xmlns:yed="http://www.yworks.com/xml/yed/3">', '  <key for="node" id="d1" yfiles.type="nodegraphics"/>', '  <graph edgedefault="directed" id="G">']
graph = open("graph.graphml", 'w')
for line in title:
	print >>graph, line
fout = open('users.csv', 'w')
fout.write('id,name,sex,bdate,age,city,university,count_posts,count_reposts\n')
users=[]
for i in range (len(publics_list['public_ids'])):
	offset = 0;
	url = 'https://api.vk.com/method/groups.getMembers?fields=name&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_ids'][i])
	members = urllib2.urlopen(url).read()
	members = json.loads(members)
	sleep(0.4)
	members_count = members['response']['count']
	while True:
		url = 'https://api.vk.com/method/groups.getMembers?fields=name,sex,bdate,city,universities&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_ids'][i])
		members = urllib2.urlopen(url).read()
		members = json.loads(members)
		sleep(0.4)
		for member in members['response']['users']:
			if not (member['uid'] in users):
				users.append(member['uid'])
				print member['uid']

				age = '-'
				bdate = '-'
				city = '-'
				if 'bdate' in member:
					bdate = member['bdate']
					date = member['bdate'].split('.')
					if len(date) == 3:
						birth_date = datetime(int(date[2]), int(date[1]), int(date[0]))
						curr_time = datetime.now()
						age = int((curr_time - birth_date).days/365.2425)
				if 'city' in member and member['city'] != 0:
					print 'getting city...'
					city_info = 'https://api.vk.com/method/database.getCitiesById?access_token=' + access_token + '&city_ids=' + str(member['city'])
					city_info = urllib2.urlopen(city_info).read()
					print 'got city'
					city_info = json.loads(city_info)
					sleep(0.4)
					city =  city_info['response'][0]['name']
				university = ''
				if 'universities' in member:
					for c in range(0, len(member['universities'])):
						university += str(c+1) + ') '
						if 'name' in member['universities'][c]:
							university = member['universities'][c]['name']
						if 'faculty_name' in member['universities'][c]:
							university += ', ' + member['universities'][c]['faculty_name']
						if 'graduation' in member['universities'][c]:
							if member['universities'][c]['graduation'] != 0:
								university += ', ' + str(member['universities'][c]['graduation'])
						university += '. '

				wall_count = 100
				date_diff = timedelta(1)
				wall_offset = 0
				wall_count = 101
				count_original = 0
				count_reposts = 0
				while (wall_offset < wall_count and date_diff.days < 366):
					print 'getting wall'
					wall = 'https://api.vk.com/method/wall.get?access_token=' + access_token + '&filter=owner&offset=' + str(wall_offset) + '&count=100&owner_id=' + str(member['uid'])
					wall = urllib2.urlopen(wall).read()
					print 'got wall'
					wall = json.loads(wall)
					sleep(0.4)
					if 'response' in wall:
						wall_count = wall['response'][0]
						del wall['response'][0]
						for post in wall['response']:
							post_date = datetime.fromtimestamp(post['date'])
							date_diff = curr_time - post_date
							if date_diff.days < 366:
								if post['post_type'] == 'post':
									count_original +=1
								else:
									count_reposts += 1
						wall_offset += 100
					else:
						wall_count = 0

				fout.write('%d,%s,%s,%s,%s,%s,%s,%d,%d\n' % (member['uid'], member['first_name'].encode("utf-8") + ' ' + member['last_name'].encode("utf-8"), sex[member['sex']-1], bdate, str(age), city, university, count_original, count_reposts))
				
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

fout.close()

edge_num = 0
for user in users:
	print user
	friends_url = 'https://api.vk.com/method/friends.get?access_token=' + access_token + '&fields=name&user_id=' + str(user)
	friends = urllib2.urlopen(friends_url).read()
	friends = json.loads(friends)
	sleep(0.4)
	if ('response' in friends):
		for friend in friends['response']:
			if (friend['uid'] > user):
				if (friend['uid'] in users):
					print >>graph, '<edge id="e' + str(edge_num) + '" source="' + str(user) + '" target="' + str(friend['uid']) + '"/>'
					edge_num += 1
print >>graph, '  </graph>'
print >>graph, '</graphml>'
