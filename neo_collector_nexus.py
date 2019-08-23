#!usr/bin/env python
import datetime
import gatherdata_multithread
import createwebdata
import getlcminfo
import ipfinder_integrate
import handlefiles
import dashboard_integrate
import backups_integrate
import online_status
import mirrortoserver


def nexus():

	# setting the run date in various formats

	date_block = datetime.datetime.now().strftime('%d%m%Y')
	date_dmy = datetime.datetime.now().strftime('%d/%m/%Y')

	with open('/anonymised/path.txt', 'w') as neo:
		gatherdata_multithread.gather(date_block)
		neo.write('1')
		createwebdata.createwebdata(date_block, date_dmy)
		neo.write('2')
		getlcminfo.getlcminfo(date_block, date_dmy)
		neo.write('3')
		ipfinder_integrate.gatherinfo(date_block)
		neo.write('4')
		dashboard_integrate.dashboard_integrate()
		neo.write('5')
		backups_integrate.backups_integrate(date_block, date_dmy)
		neo.write('6')
		online_status.online_status(date_block, date_dmy)
		neo.write('7')
		handlefiles.handlefiles(date_block)
		neo.write('8')
		mirrortoserver.mirrortoserver(date_block)
		neo.write('9')


if __name__ == '__main__':
	nexus()
