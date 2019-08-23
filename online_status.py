#!usr/bin/env python
import datetime
import os
import sys
sys.path.append('/anonymised/path')
import jsoncommands


def online_status(todaydate, datedmy):
	reportfileloc = '/anonymised/path/' + todaydate + '_gather.txt'
	endloc = '/anonymised/path.json'
	endjson = {}
	with open(reportfileloc, 'r') as reportfile:
		report = reportfile.readlines()
	for x in range(1, len(report)):
		# skipping first line
		splitline = report[x].split(',')
		splitline = [x.upper().strip() for x in splitline]
		if not splitline[0] in endjson.keys():
			endjson[splitline[0]] = []
		data = [splitline[1], splitline[2], splitline[3]]
		endjson[splitline[0]].append(data)
	endjson['polltime'] = datedmy
	jsoncommands.writejson(endjson, endloc)


if __name__ == '__main__':

	if raw_input('Type debug to enable debug mode.\n>') == 'debug':
		todaydate_raw = datetime.datetime.now() - datetime.timedelta(days=1)
	else:
		todaydate_raw = datetime.datetime.now()

	todaydate = todaydate_raw.strftime('%d%m%Y')
	todaydmy = todaydate_raw.strftime('%d/%m/%Y')

	online_status(todaydate, todaydmy)
