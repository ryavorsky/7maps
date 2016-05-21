#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
from time import sleep
from datetime import datetime, timedelta
import vk_auth
import sys
import csv
import os
import shutil

def get_json(url):
	getjson = urllib.request.urlopen(url).readall().decode('utf-8')
	getjson = json.loads(getjson)
	sleep(0.3)
	return getjson

app_ids = ['5396820','5397060','5399458','5399462','5399464','5401636','5401637','5406910']
app_id = '5397060'

count_downloaded = 0

sex = ['F', 'M']
cities = {1:"Москва",2:"Санкт-Петербург"}

publics_list = open('../config/config.json').read()
publics_list = json.loads(publics_list)

count_total_people_to_be_downloaded = 0
if (len(sys.argv) == 2):
	file_name = '../results/csv/members_' + str(publics_list['public_id'][0]) + '_' + sys.argv[1] + '-end.csv'
elif (len(sys.argv) >= 3):
	count_total_people_to_be_downloaded = int(sys.argv[2])
	file_name = '../results/csv/members_' + str(publics_list['public_id'][0]) + '_' + sys.argv[1] + '-' + str(int(sys.argv[1]) + int(sys.argv[2])) + '.csv'
	if (len(sys.argv) == 4):
		app_id = app_ids[int(sys.argv[3])]
else:
	file_name = '../results/csv/members_' + str(publics_list['public_id'][0]) + '.csv'
fout = open(file_name, 'w')
if not(os.path.exists('../logs/' + 'members_info_' + str(publics_list['public_id'][0]))):
	os.mkdir('../logs/' + 'members_info_' + str(publics_list['public_id'][0]))
logs = open(file_name.replace('members','log_members').replace('results/csv','logs/' + 'members_info_' + str(publics_list['public_id'][0])), 'w')
csvwriter = csv.writer(fout)
logwriter = csv.writer(logs)

csvwriter.writerows([['№','id','link','name','sex','bdate','age','city','university','count_unique_posts','count_reposts','count_likes','count_comments','count_unique_reposts','count_friends','count_followers']])
logwriter.writerows([['type', 'uid']])

users=[]

access_token = vk_auth.auth('vktool@mail.ru', 'vkpassvk', app_id, 'offline')[0]

print (access_token)

offset = 0
number = 0

if (len(sys.argv) > 1):
	offset = int(sys.argv[1])
	number = int(sys.argv[1])
if (len(sys.argv) > 2):
	count_people_to_download = int(sys.argv[2])

url = 'https://api.vk.com/method/groups.getMembers?fields=name&access_token=' + access_token + '&count=1&offset=' + str(offset) + '&group_id=' + str(publics_list['public_id'][0])
members = get_json(url)
try:
	members = get_json(url)
except:
	print ('failed getting members')
if ('response' in members):
	members_count = members['response']['count']
	if (len(sys.argv) == 1):
		count_total_people_to_be_downloaded = members_count
	if (len(sys.argv) == 2):
		count_total_people_to_be_downloaded = members_count - int(sys.argv[1])


while True:
	url = 'https://api.vk.com/method/groups.getMembers?fields=name,sex,bdate,city,universities&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_id'][0])
	try:
		members = get_json(url)
	except:
		print ('failed getting members')
	if 'response' in members:
		for member in members['response']['users']:

			count_downloaded += 1

			if (len(sys.argv) > 2):
				if (sys.argv[2] != '0'):
					if (count_downloaded == count_people_to_download + 1):
						fout.close()
						sys.exit()

			if (count_downloaded % 25 == 0):
				fout.close()
				logs.close()
				fout = open(file_name, 'a')
				csvwriter = csv.writer(fout)
				logs = open(file_name.replace('members','log_members').replace('results/csv','logs/' + 'members_info_' + str(publics_list['public_id'][0])), 'a')
				logwriter = csv.writer(logs)

			users.append(member['uid'])

			print ('Processing user №' + str(count_downloaded) + ' out of ' + str(count_total_people_to_be_downloaded) + ' (id ' + str(member['uid']) + ')')

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
					if (member['city']) >= 0:
						city_info = 'https://api.vk.com/method/database.getCitiesById?access_token=' + access_token + '&city_ids=' + str(member['city'])
						try:
							city_info = get_json(city_info)
						except:
							print ('Failed getting city__id' + str(member['uid']))
							logwriter.writerows([['city', str(member['uid'])]])
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
			while (wall_offset < wall_count and date_diff.days < 366):
				wall = 'https://api.vk.com/method/wall.get?access_token=' + access_token + '&filter=owner&offset=' + str(wall_offset) + '&count=100&owner_id=' + str(member['uid'])
				try:
					wall = get_json(wall)
				except:
					logwriter.writerows([['wall', str(member['uid'])]])
					print ('Failed getting wall__id' + str(member['uid']))
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
			count_friends = 0
			friends_url = 'https://api.vk.com/method/friends.get?access_token=' + access_token + '&fields=name&user_id=' + str(member['uid'])
			try:
				friends = get_json(friends_url)
			except:
				logwriter.writerows([['friends', str(member['uid'])]])
				print ('Failed getting friends__id' + str(member['uid']))
			if ('response' in friends):
				count_friends = len(friends['response'])
				if (count_friends == 5000):
					friends_url = 'https://api.vk.com/method/friends.get?offset=5000&access_token=' + access_token + '&fields=name&user_id=' + str(member['uid'])
					try:
						friends = get_json(friends_url)
					except:
						logwriter.writerows([['friends', str(member['uid'])]])
						print ('Failed grtting friends__id' + str(member['uid']))
					if ('response' in friends):
						count_friends += len(friends['response'])

			count_followers = 0
			followers_url = 'https://api.vk.com/method/users.getFollowers?access_token=' + access_token + '&count=0&user_id=' + str(member['uid'])
			try:
				followers = get_json(followers_url)
			except:
				logwriter.writerows([['followers', str(member['uid'])]])
				print ('Failed getting followers__id' + str(member['uid']))
			if ('response' in followers):
				count_followers = followers['response']['count']
			csvwriter.writerows([[number, member['uid'], 'http://vk.com/id' + str(member['uid']), str(member['first_name'] + ' ' + member['last_name']), str(sex[member['sex']-1]), str(bdate), str(age), str(city), str(university), count_original, count_reposts, count_likes, count_comments,count_unique_reposts,count_friends,count_followers]])
			number += 1

	if (offset + 1000 > members_count):
		break
	offset += 1000

fout.close()
logs.close()