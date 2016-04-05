#! /usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import urllib
import json
from time import sleep
import vk_auth
from datetime import datetime, timedelta

def get_json(url):
	getjson = urllib.request.urlopen(url).readall().decode('utf-8')
	getjson = json.loads(getjson)
	sleep(0.25)
	return getjson

app_id = '5397060'
access_token = vk_auth.auth('vktool@mail.ru', 'vkpassvk', app_id, 'offline')[0]
print (access_token)

count_downloaded = 0

publics_list = open('../config/publics.json').read()
publics_list = json.loads(publics_list)

fout = open('../results/csv/groups_' + str(publics_list['public_ids'][0]) + '.csv', 'w')
csvwriter = csv.writer(fout)
csvwriter.writerows([['id','name','description','count_members', 'count_posts']])
users=[]


offset = 0;
url = 'https://api.vk.com/method/groups.getMembers?fields=name&access_token=' + access_token + '&count=1&offset=' + str(offset) + '&group_id=' + str(publics_list['public_ids'][0])
members = get_json(url)
try:
	members = get_json(url)
except:
	print ('failed')
if ('response' in members):
	members_count = members['response']['count']
while True:
	url = 'https://api.vk.com/method/groups.getMembers?fields=name,sex,bdate,city,universities&access_token=' + access_token + '&count=1000&offset=' + str(offset) + '&group_id=' + str(publics_list['public_ids'][0])
	try:
		members = get_json(url)
	except:
		print ('failed')
	if 'response' in members:
		for member in members['response']['users']:
			if not (member['uid'] in users):
				users.append(member['uid'])
				print (member['uid'])
	if (offset + 1000 > members_count):
		break
	offset += 1000

group_list = []
for user in users:
	group_url = 'https://api.vk.com/method/groups.get?access_token=' + access_token + '&extended=1&count=1000&user_id=' + str(user)
	try:
		groups = get_json(group_url)
	except:
		print ('failed')
	if ('response' in groups):
		del groups['response'][0]
		for group in groups['response']:
			if (group['gid'] not in group_list):

				count_downloaded += 1
				if (count_downloaded % 25 == 0):
					fout.close()
					fout = open('../results/csv/groups.csv', 'a')
					csvwriter = csv.writer(fout)

				print (group['gid'])
				wall = 'https://api.vk.com/method/wall.get?access_token=' + access_token + '&filter=owner&offset=0&count=1&owner_id=-' + str(group['gid'])
				try:
					wall = get_json(wall)
				except:
					print ('failed')
				if 'response' in wall:
					count_posts = wall['response'][0]

				group_list.append(group['gid'])
				group_info = 'https://api.vk.com/method/groups.getById?group_id=' + str(group['gid']) + '&fields=description,members_count'
				try:
					group_info = get_json(group_info)
				except:
					print ('failed')
				if ('response' in group_info):
					for group in group_info['response']:
						description = ''
						members_count = 0
						name = ''
						if ('name' in group):
							name = group['name']
							name = name.replace(';', ':')
						if ('description' in group):
							description = group['description']
							description = description.replace(';', ':')
						if ('members_count' in group):
							members_count = group['members_count']
						csvwriter.writerows([[group['gid'], name, description, str(members_count), count_posts]])
fout.close()