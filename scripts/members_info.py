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

print (access_token)

sex = ['F', 'M']
cities = {1:"Москва",2:"Санкт-Петербург"}

publics_list = open('../config/publics.json').read()
publics_list = json.loads(publics_list)

fout = open('../results/csv/members.csv', 'w')
fout.write('id,link,name,sex,bdate,age,city,university,count_unique_posts,count_reposts,count_likes,count_comments,count_unique_reposts,count_friends,count_followers\n')
users=[]
for i in range (len(publics_list['public_ids'])):
	offset = 0;
	url = 'https://api.vk.com/method/groups.getMembers?fields=name&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_ids'][i])
	members = get_json(url)
	try:
		members = get_json(url)
	except:
		print ('failed')
	members_count = members['response']['count']
	while True:
		url = 'https://api.vk.com/method/groups.getMembers?fields=name,sex,bdate,city,universities&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_ids'][i])
		try:
			members = get_json(url)
		except:
			print ('failed')
		if 'response' in members:
			for member in members['response']['users']:
				if not (member['uid'] in users):
					users.append(member['uid'])
					print ('info ' + str(member['uid']))

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
						if (member['city'] in cities):
							city = cities[member['city']]
						else:
							city_info = 'https://api.vk.com/method/database.getCitiesById?access_token=' + access_token + '&city_ids=' + str(member['city'])
							try:
								city_info = get_json(city_info)
							except:
								print ('failed')
							if 'response' in city_info:
								city =  city_info['response'][0]['name']
					university = ''
					if 'universities' in member:
						for c in range(0, len(member['universities'])):
							university += str(c+1) + ') '
							if 'name' in member['universities'][c]:
								university += member['universities'][c]['name']
							if 'faculty_name' in member['universities'][c]:
								university += '-' + member['universities'][c]['faculty_name']
							if 'graduation' in member['universities'][c]:
								if member['universities'][c]['graduation'] != 0:
									university += '-' + str(member['universities'][c]['graduation'])
							university += '. '
							university = university.replace(',', '.')
							university = university.replace("\n", "")
							university = university.replace("\r", "")
					curr_time = datetime.now()
					date_diff = timedelta(1)
					wall_offset = 0
					wall_count = 101
					count_original = 0
					count_reposts = 0
					count_likes = 0
					count_comments = 0
					count_unique_reposts = 0
					unique_comment_authors = []
					while (wall_offset < wall_count and date_diff.days < 366):
						wall = 'https://api.vk.com/method/wall.get?access_token=' + access_token + '&filter=owner&offset=' + str(wall_offset) + '&count=100&owner_id=' + str(member['uid'])
						try:
							wall = get_json(wall)
						except:
							print ('failed')
						if 'response' in wall:
							wall_count = wall['response'][0]
							del wall['response'][0]
							for post in wall['response']:
								post_date = datetime.fromtimestamp(post['date'])
								date_diff = curr_time - post_date
								if date_diff.days < 366:
									count_likes += post['likes']['count']
									count_comments += post['comments']['count']
									if post['post_type'] == 'post':
										count_original +=1
										count_unique_reposts += post['reposts']['count']
									else:
										count_reposts += 1

							wall_offset += 100
						else:
							wall_count = 0

					unique_comment_authors = len(unique_comment_authors)

					count_friends = 0
					friends_url = 'https://api.vk.com/method/friends.get?access_token=' + access_token + '&fields=name&user_id=' + str(member['uid'])
					try:
						friends = get_json(friends_url)
					except:
						print ('failed')
					if ('response' in friends):
						count_friends = len(friends['response'])

					count_followers = 0
					followers_url = 'https://api.vk.com/method/users.getFollowers?access_token=' + access_token + '&count=0&user_id=' + str(member['uid'])
					try:
						followers = get_json(followers_url)
					except:
						print ('failed')
					if ('response' in followers):
						count_followers = followers['response']['count']
					fout.write('%d,%s,%s,%s,%s,%s,%s,%s,%d,%d,%d,%d,%d,%d,%d\n' % (member['uid'], 'http://vk.com/id' + str(member['uid']), str(member['first_name'] + ' ' + member['last_name']), str(sex[member['sex']-1]), str(bdate), str(age), str(city), str(university), count_original, count_reposts, count_likes, count_comments,count_unique_reposts,count_friends,count_followers))

		if (offset + 1000 > members_count):
			break
		offset += 1000

fout.close()
