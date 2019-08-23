#!usr/bin/env python
import csv
import datetime
import os
import re
import sys
sys.path.append('/anonymised/path')
import jsoncommands


def gatherinfo(todaydate):

	# globals

	ippattern = r'ip address (\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3})'
	backupdir = '/anonymised/path'
	ipfinderdir = '/anonymised/path'
	integratefile = ipfinderdir + os.sep + 'neo_collectoranonymised_file_0'

	# getting existing ipfinder entries

	existingips = []
	for ipfinder in os.listdir(ipfinderdir):
		if 'neo_collector' in ipfinder:
			continue
		csvloc = ipfinderdir + os.sep + ipfinder
		with open(csvloc, 'r') as ip_raw:
			ip_csv = csv.reader(ip_raw, delimiter=",")
			for ipline in ip_csv:
				if len(ipline) > 1:
					existingip = ipline[2]
					if '/32' in existingip:
						existingip = existingip.replace('/32', '')
					existingips.append(existingip)

	# collecting data

	neodata = []
	validdir = backupdir + os.sep + todaydate
	types = os.listdir(validdir)
	for type in types:
		datadir = backupdir + os.sep + todaydate + os.sep + type
		for dataloc in os.listdir(datadir):
			hostname = dataloc.split('.')[1]
			hostadded = 0
			newdatalist = []
			datapath = datadir + os.sep + dataloc
			with open(datapath, 'r') as datafile:
				data = datafile.readlines()
				interfacescan = False
				interface = ''
				ipaddress = ''
				for dataline in data:
					if dataline.startswith('interface'):
						interface = dataline.split(' ')[1].strip()
						interfacescan = True
					elif dataline.startswith('!'):
						if interface and ipaddress and not ipaddress in existingips:  # prevents duplication
							# process
							newdatalist.append({'host': hostname, 'platform': 'Cisco', 'ip': ipaddress,
												'type': 'Interface', 'interface': interface, 'logical': type})
							hostadded += 1
							interface = ''
							ipaddress = ''
						interfacescan = False
					elif interfacescan:
						if re.search(ippattern, dataline):
							ipaddress = re.search(ippattern, dataline).group(1)
			if hostadded > 0:
				for newdata in newdatalist:
					neodata.append(newdata)

	with open(integratefile, 'w') as raw_integrate:
		csv_integrate = csv.writer(raw_integrate, delimiter=",")
		csv_integrate.writerow(['# Host', 'Platform' , 'IP' , 'Type' , 'Interface', 'Logical System'])
		for neo in neodata:
			csvrow = [neo['host'], neo['platform'], neo['ip'], neo['type'], neo['interface'], neo['logical']]
			csv_integrate.writerow(csvrow)


if __name__ == '__main__':

	if raw_input('Type debug to enable debug mode.') == 'debug':
		todaydate = datetime.datetime.now() - datetime.timedelta(days=1)
	else:
		todaydate = datetime.datetime.now()

	todaydate = todaydate.strftime('%d%m%Y')

	gatherinfo(todaydate)
