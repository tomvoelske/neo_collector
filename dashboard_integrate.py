#!usr/bin/env python
import os
import sys
import datetime
sys.path.append('/anonymised/path')
import jsoncommands


def dashboard_integrate():

	# globals

	lcmpath = '/anonymised/path.json'
	datadir = '/anonymised/path'
	interdir = '/anonymised/path/intermediate'

	lcmdict = jsoncommands.readjson(lcmpath)
	lcmsources = lcmdict.keys()
	additions = 0
	changes = 0

	for lcmsource in lcmsources:
		existinghosts = []
		lcmhosts = [x['hostname'] for x in lcmdict[lcmsource]]
		existingdatasrc = datadir + os.sep + 'dashboard_' + lcmsource + '.json'
		existingdict = jsoncommands.readjson(existingdatasrc)
		existingexcerpt = existingdict['data']

		# modifying existing hosts

		for existingindex, existingdata in enumerate(existingexcerpt):
			existinghost = existingdata['hostname']
			existinghosts.append(existinghost)
			if existinghost in lcmhosts:
				# update
				lcmindex = lcmhosts.index(existinghost)
				lcmdata = lcmdict[lcmsource][lcmindex]
				for category in lcmdata:
					if category != 'hostname' and lcmdata[category] and lcmdata[category] != 'UNKNOWN':
						try:
							if existingdict['data'][existingindex][category] != lcmdata[category]:
								existingdict['data'][existingindex][category] = lcmdata[category]
								changes += 1
						except KeyError:
							existingdict['data'][existingindex][category] = lcmdata[category]
							changes += 1

		# adding new hosts

		for lcmindex, lcmhost in enumerate(lcmhosts):
			if not lcmhost in existinghosts:
				existingdict['data'].append(lcmdict[lcmsource][lcmindex])
				additions += 1

		# outputting

		existingdict['polltime'] = datetime.datetime.today().strftime('%d/%m/%Y')

		outputpath = interdir + os.sep + 'dashboard_' + lcmsource + '.json'
		jsoncommands.writejson(existingdict, outputpath)


	print(additions)
	print(changes)

	flagjson = jsoncommands.readjson('/anonymised/path/intermediate/flags.json')
	flagjson['neo'] = 1
	jsoncommands.writejson(flagjson, '/anonymised/path/intermediate/flags.json')


if __name__ == '__main__':
	dashboard_integrate()
