#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
from time import sleep
from datetime import datetime, timedelta
import sys
import csv
import os
import vk_auth

app_id = '5397060'
access_token = vk_auth.auth('vktool@mail.ru', 'vkpassvk', app_id, 'offline')[0]
print (access_token)

def get_json(url):
	getjson = urllib.request.urlopen(url).readall().decode('utf-8')
	getjson = json.loads(getjson)
	sleep(0.3)
	return getjson

publics_list = open('../../config/config.json').read()
publics_list = json.loads(publics_list)

logs_folder = '../../logs/' + publics_list['fail_checker_logs_folder'][0]
logs = os.listdir(logs_folder)

count_fails = 0
fails_corrected = 0

for log in logs:
	curr_log = open('../../logs/' + publics_list['fail_checker_logs_folder'][0] + '/' + log)
	curr_log_reader = csv.reader(curr_log)
	result_before = open('../../results/csv/' + log[4:], 'r')
	result_before_reader = csv.reader(result_before)

	result_after = open(('../../results/csv/' + log[4:]).replace('.csv', '_tmp.csv'), 'w')
	result_after_writer = csv.writer(result_after)

	logs_after = open('../../logs/' + publics_list['fail_checker_logs_folder'][0] + '/tmp_' + log, 'w')
	logs_after_writer = csv.writer(logs_after)
	logs_after_writer.writerows([['type', 'uid']])


	next(curr_log_reader)

	failed_users = {}
	for row in curr_log_reader:
		failed_users[row[1]] = []
	curr_log.seek(0)
	next(curr_log_reader)
	for row in curr_log_reader:
		count_fails += 1
		failed_users[row[1]].append(row[0])

	for row in result_before_reader:
		if (row[1] not in failed_users):
			result_after_writer.writerows([[row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15]]])
		else:
			print ('Checking id' + row[1])
			city = row[7]
			count_original = row[9]
			count_reposts = row[10]
			count_likes = row[11]
			count_comments = row[12]
			count_unique_reposts = row[13]
			count_friends = row[14]
			count_followers = row[15]

			if ('city' in failed_users[row[1]]):
				url = 'https://api.vk.com/method/users.get?fields=city&user_ids=' + row[1] + '&access_token=' + access_token
				try:
					user_info = get_json(url)
				except:
					print ('Failed getting city__' + str(row[1]))
					logs_after_writer .writerows([['city', str(member['uid'])]])
				if ('response' in user_info):
					city_code = user_info['response'][0]['city']
					city_info = 'https://api.vk.com/method/database.getCitiesById?access_token=' + access_token + '&city_ids=' + str(city_code)
					try:
						city_info = get_json(city_info)
					except:
						print ('failed getting city__' + str(member['uid']))
						logs_after_writer.writerows([['city', str(member['uid'])]])
					if 'response' in city_info:
						city =  city_info['response'][0]['name']
				fails_corrected += 1

			if ('wall' in failed_users[row[1]]):
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
					wall = 'https://api.vk.com/method/wall.get?access_token=' + access_token + '&filter=owner&offset=' + str(wall_offset) + '&count=100&owner_id=' + str(row[1])
					try:
						wall = get_json(wall)
					except:
						print ('failed getting wall__' + str(member['uid']))
						logs_after_writer.writerows([['wall', str(member['uid'])]])
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
				fails_corrected += 1

			if ('friends' in failed_users[row[1]]):
				count_friends = 0
				friends_url = 'https://api.vk.com/method/friends.get?access_token=' + access_token + '&fields=name&user_id=' + str(row[1])
				try:
					friends = get_json(friends_url)
				except:
					print ('failed getting friends__' + str(member['uid']))
					logs_after_writer.writerows([['friends', str(member['uid'])]])
				if ('response' in friends):
					count_friends = len(friends['response'])
					if (count_friends == 5000):
						friends_url = 'https://api.vk.com/method/friends.get?offset=5000&access_token=' + access_token + '&fields=name&user_id=' + str(row[1])
						try:
							friends = get_json(friends_url)
						except:
							print ('failed grtting friends__' + str(member['uid']))
							logs_after_writer.writerows([['friends', str(member['uid'])]])
						if ('response' in friends):
							count_friends += len(friends['response'])
				fails_corrected += 1

			if ('followers' in failed_users[row[1]]):
				count_followers = 0
				followers_url = 'https://api.vk.com/method/users.getFollowers?access_token=' + access_token + '&count=0&user_id=' + str(row[1])
				try:
					followers = get_json(followers_url)
				except:
					logs_after_writer.writerows([['followers', str(member['uid'])]])
					print ('failed getting followers__' + str(member['uid']))
				if ('response' in followers):
					count_followers = followers['response']['count']
				fails_corrected += 1

			result_after_writer.writerows([[row[0],row[1],row[2],row[3],row[4],row[5],row[6],city,row[8],count_original,count_reposts,count_likes,count_comments,count_unique_reposts,count_friends,count_followers]])
 

curr_log.close()
result_before.close()
result_after.close()
logs_after.close()

os.remove('../../logs/' + publics_list['fail_checker_logs_folder'][0] + '/' + log)
os.rename('../../logs/' + publics_list['fail_checker_logs_folder'][0] + '/tmp_' + log, '../../logs/' + publics_list['fail_checker_logs_folder'][0] + '/' + log)

os.remove('../../results/csv/' + log[4:])
os.rename(('../../results/csv/' + log[4:]).replace('.csv', '_tmp.csv'), '../../results/csv/' + log[4:])

print ('Completed. ' + str(fails_corrected) + ' errors out of ' + str(count_fails) + ' were corrected') 