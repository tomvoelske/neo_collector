#!usr/bin/env python
import datetime
import os
import sys
sys.path.append('/anonymised/path')
import jsoncommands


def backups_integrate(todaydate, datedmy):
	rootdir = '/anonymised/path/' + todaydate
	endloc = '/anonymised/path.json'
	backupjson = {}
	for dir in os.listdir(rootdir):
		environment = dir.upper()
		backupjson[environment] = []
		environmentpath = rootdir + os.sep + dir
		backuplist = os.listdir(environmentpath)
		for backup in backuplist:
			hostname = backup.split('.')[1].upper()
			backupjson[environment].append({'date': datedmy, 'host': hostname})
	jsoncommands.writejson(backupjson, endloc)


if __name__ == '__main__':

	if raw_input('Type debug to enable debug mode.\n>') == 'debug':
		todaydate_raw = datetime.datetime.now() - datetime.timedelta(days=1)
	else:
		todaydate_raw = datetime.datetime.now()

	todaydate = todaydate_raw.strftime('%d%m%Y')
	todaydmy = todaydate_raw.strftime('%d/%m/%Y')

	backups_integrate(todaydate, todaydmy)
