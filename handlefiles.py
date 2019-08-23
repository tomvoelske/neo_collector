#!usr/bin/env python
import datetime
import os
import shutil
import sys
import zipfile


def handlefiles(todaydate, debug=False):

	# base variables

	backupdir = '/anonymised/path'
	reportdir = '/anonymised/path'
	validdir = backupdir + os.sep + todaydate
	ziplocation = backupdir + os.sep + 'neo_collector_' + todaydate

	if not debug:

		# generates initial archive

		shutil.make_archive(ziplocation, 'zip', validdir)

		# list of report files to add, which are then sought and added

		validreports = [reportdir + os.sep + todaydate + '_errors.txt', reportdir + os.sep + todaydate + '_gather.txt']
		existingzip = zipfile.ZipFile(ziplocation + '.zip', 'a', zipfile.ZIP_DEFLATED)
		for report in validreports:
			existingzip.write(report, os.path.basename(report))
		existingzip.close()

	# copies elsewhere - currently inactive

	# deletes old uncompressed directories

	inventory = os.listdir(backupdir)

	for dir in inventory:
		if 'zip' in dir:
			if not todaydate in dir:
				os.remove(backupdir + os.sep + dir)
		else:
			if dir != todaydate:
				shutil.rmtree(backupdir + os.sep + dir)

	# deletes old reports, if they are over a week old

	safeprefixes = [todaydate]
	for x in range(1, 7):
		safeprefixes.append((datetime.datetime.now() - datetime.timedelta(days=x)).strftime('%d%m%Y'))

	inventory = os.listdir(reportdir)

	for report in inventory:
		reportsafe = False
		for safeprefix in safeprefixes:
			if safeprefix in report:
				reportsafe = True
				break

		if not reportsafe:
			os.remove(reportdir + os.sep + report)


if __name__ == '__main__':

	if raw_input('Type debug to enable debug mode.\n>') == 'debug':
		todaydate = datetime.datetime.now() - datetime.timedelta(days=1)
	else:
		todaydate = datetime.datetime.now()

	todaydate = todaydate.strftime('%d%m%Y')

	if len(sys.argv) == 1:
		handlefiles(todaydate)
	elif sys.argv[1] == 'test':
		handlefiles(todaydate, True)
