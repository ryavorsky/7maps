import re
import os
import json
import csv

publics_list = open('../../config/config.json').read()
publics_list = json.loads(publics_list)
public_id = publics_list['csv_builder'][0]

new_csv = open('members_' + str(public_id) + ".csv", 'w')
new_csv_writer = csv.writer(new_csv)

new_csv_writer.writerows([['№','id','link','name','sex','bdate','age','city','university','count_unique_posts','count_reposts','count_likes','count_comments','count_unique_reposts','count_friends','count_followers']])


csv_files = os.listdir('.')

files_to_be_joined = []

for file in csv_files:
	if (re.match(r"^members_" + str(public_id) + "_", file) is not None):
		files_to_be_joined.append(file)

files_to_be_joined.sort(key=lambda x:int(x.split('_')[-1][:-4].split('-')[0]))

for file in files_to_be_joined:
	curr_csv = open(file, 'r')
	curr_csv_reader = csv.reader(curr_csv)
	next(curr_csv_reader)
	for row in curr_csv_reader:
		new_csv_writer.writerows([row])
	curr_csv.close()


new_csv.close()