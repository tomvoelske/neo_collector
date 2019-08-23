#!usr/bin/env python
import datetime
import os
import re
import sys
sys.path.append('/anonymised/path')
import jsoncommands


def getlcminfo(todaydate, backupdate):

	# globals

	rootdir = '/anonymised/path/' + todaydate
	endpath = '/anonymised/path.json'

	# RegEx

	softwarepatterns = ['IOS', 'software, version']  # IOS, catOS
	versionpatterns = ['IOS.*Version ([\w.()]+),?', 'Version NmpSW: ([\w.()]+)']
	hardwarepatterns = ['Cisco ([\w./-]+) .* processor', 'Model: ([\w./-]+)', 'Cisco ([\w./-]+) .* bytes of memory']
	specifichardwarepatterns = ['Cisco [\w.\/-]+ [(](.*)[)] processor']
	serialpatterns = ['System serial number\s*: (\w+)', 'Processor board ID (\w+)',
					  'Hardware Version: .*  Model: .*  Serial #: (\w+)']
	lastrebootpatterns = ['uptime is (.*)', 'Uptime is (.*)']

	newjson = {}

	sources = os.listdir(rootdir)
	found = 0
	notfound = 0

	for source in sources:
		sourcedir = rootdir + os.sep + source
		newjson[source] = []
		filelist = os.listdir(sourcedir)
		for file in filelist:
			found += 1
			hostname = file.split('.')[1].upper()
			ipaddr = file.split('.')[0].replace('_', '.')
			newdata = {'hostname': hostname, 'software_type': '', 'software_version': '', 'ip_address': ipaddr,
					   'hardware': '', 'hardware_specific': '', 'serial_number': '', 'last_reboot': '', 'uptime': -1,
					   'last_backup': backupdate, 'days_elapsed': 0}
			dataloc = sourcedir + os.sep + file
			with open(dataloc, 'r') as datafile:
				datalines = datafile.readlines()
				for dataline in datalines:
					if not newdata['software_type']:
						if re.search(softwarepatterns[0], dataline, re.IGNORECASE):
							newdata['software_type'] = 'IOS'
						elif re.search(softwarepatterns[1], dataline, re.IGNORECASE):
							newdata['software_type'] = 'CATOS'
					checkregex(versionpatterns, dataline, 'software_version', newdata)
					checkregex(hardwarepatterns, dataline, 'hardware', newdata)
					checkregex(specifichardwarepatterns, dataline, 'hardware_specific', newdata)
					checkregex(serialpatterns, dataline, 'serial_number', newdata)
					checkregex(lastrebootpatterns, dataline, 'last_reboot', newdata)

			# handling information
			extractnum = '(\d+)'

			if newdata['last_reboot']:
				fulluptime = newdata['last_reboot'].split(',')
				newdata['last_reboot'] = ''  # just in case it somehow fails
				totaluptime = 0
				for uptimepart in fulluptime:
					magnitude = int(re.search(extractnum, uptimepart).group(1))
					if magnitude:
						if 'year' in uptimepart.lower():
							totaluptime += magnitude * 365
						if 'month' in uptimepart.lower():
							totaluptime += magnitude * 30
						if 'week' in uptimepart.lower():
							totaluptime += magnitude * 7
						if 'day' in uptimepart.lower():
							totaluptime += magnitude
				newdata['last_reboot'] = (datetime.datetime.now() - datetime.timedelta(days=totaluptime)).strftime('%d/%m/%Y')
				newdata['uptime'] = totaluptime

			if not newdata['software_version'] or not newdata['hardware'] or not newdata['serial_number'] \
			or not newdata['last_reboot']:
				print(hostname + ' did not find all info @ ' + source)
				print(newdata)
				found -= 1
				notfound += 1

			newjson[source].append(newdata)

	jsoncommands.writejson(newjson, endpath)
	print('Found: ' + str(found))
	print('Not Found: ' + str(notfound))


def checkregex(patterns, dataline, category, newdata):
	if newdata[category]:
		return
	for pattern in patterns:
		if re.search(pattern, dataline, re.IGNORECASE):
			result = re.search(pattern, dataline, re.IGNORECASE).group(1)
			if not '0x' in result:  # don't want hex
				newdata[category] = result
				return


if __name__ == '__main__':

	if raw_input('Type debug to enable debug mode.\n>') == 'debug':
		now = datetime.datetime.now() - datetime.timedelta(days=1)
	else:
		now = datetime.datetime.now()

	todaydate = now.strftime('%d%m%Y')
	backupdate = now.strftime('%d/%m/%Y')

	getlcminfo(todaydate, backupdate)
