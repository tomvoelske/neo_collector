#!usr/bin/env python
import jsoncommands
import datetime


def createwebdata(todaydate, datadate):
	backupdata = '/anonymised/path.json'
	backupjson = jsoncommands.readjson(backupdata)

	rootfolder = '/anonymised/path'
	reportfolder = rootfolder + '/anonymised/path'
	reportdest = reportfolder + '/' + todaydate + '_gather.txt'

	successdict = {}

	with open(reportdest, 'r') as reportfile:
		report = reportfile.readlines()
	for host in report:
		hostsplit = host.split(',')
		if hostsplit[3].strip() == 'SUCCESS':
			region = hostsplit[0].upper()
			hostname = hostsplit[2].upper()
			if not region in successdict.keys():
				successdict[region] = []
			successdict[region].append({'host': hostname, 'date': datadate})

	for successkeys in successdict.keys():
		if successkeys in backupjson.keys():
			for successes in successdict[successkeys]:
				itemfound = False
				for existingindex, existingitems in enumerate(backupjson[successkeys]):
					if successes['host'] == existingitems['host']:
						backupjson[successkeys][existingindex]['date'] = successes['date']
						itemfound = True
						break
				if not itemfound:
					backupjson[successkeys].append({'host': successes['host'], 'date': successes['date']})
		else:
			backupjson[successkeys] = successdict[successkeys]

	jsoncommands.writejson(backupjson, backupdata)


if __name__ == '__main__':

	if raw_input('Type debug to enable debug mode.') == 'debug':
		now = datetime.datetime.now() - datetime.timedelta(days=1)
	else:
		now = datetime.datetime.now()

	todaydate = now.strftime('%d%m%Y')
	datadate = now.strftime('%d/%m/%Y')

	createwebdata(todaydate, datadate)
