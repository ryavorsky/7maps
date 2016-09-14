#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
from time import sleep
import vk_auth
import csv
import os

def get_json(url):
	getjson = urllib.request.urlopen(url).readall().decode('utf-8')
	getjson = json.loads(getjson)
	sleep(0.3)
	return getjson

app_id = '5397060'
access_token = vk_auth.auth('vktool@mail.ru', 'vkpassvk', app_id, 'offline')[0]
print ('Successfully logged in...')

all_groups = ['']
ids = open('../config/config.json').read()
ids = json.loads(ids)['matrix_people_list']

fout = open('../tmp/tmp_matrix.csv', 'w')
csvwriter = csv.writer(fout)
csvwriter.writerows([''])
for user_id in ids:
	print ('Processing user with id ' + str(user_id))
	curr_groups = [0] * (len(all_groups))
	curr_groups[0] = 'id' + str(user_id)

	groups_url = 'https://api.vk.com/method/groups.get?user_id=' + str(user_id) + '&access_token=' + access_token
	groups = get_json(groups_url)
	if 'response' in groups:
		for group in groups['response']:
			if group not in all_groups:
				all_groups.append(group)
				curr_groups.append(1)
			else:
				curr_groups[all_groups.index(group)] = 1
		csvwriter.writerows([curr_groups])

fout.close()

print('Finishing...')
fout = open('../results/csv/matrix.csv', 'w')
fin = open('../tmp/tmp_matrix.csv', 'r')
csvwriter = csv.writer(fout)
csvreader = csv.reader(fin)
next(csvreader)
csvwriter.writerows([all_groups])
for row in csvreader:
	new_row = [0] * (len(all_groups) - len(row))
	row.extend(new_row)
	csvwriter.writerows([row])
fout.close()
fin.close()

os.remove('../tmp/tmp_matrix.csv')