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
publics_list = open('../config/config.json').read()
publics_list = json.loads(publics_list)

url='http://api.vk.com/method/groups.getMembers?group_id=' + str(publics_list['public_id'][0])
members = get_json(url)
count_members = members['response']['count']
exit(str(count_members))
