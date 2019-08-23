#!usr/bin/env python
import datetime
import os
import pwd
import shutil
import subprocess


def mirrortoserver(todaydate):
	rootdir = '/anonymised/path/'
	destdir = '/anonymised/path'

	# deleting old copied backups
	existingfiles = os.listdir(destdir)
	todelete = [x for x in existingfiles if 'neo_collector' in x]
	for deletefile in todelete:
		os.remove(destdir + os.sep + deletefile)

	filename = 'neo_collector_' + todaydate + '.zip'
	endfilename = destdir + '/' + filename
	shutil.copy(rootdir + filename, destdir)
	anonyid = pwd.getpwnam("anonymised").pw_uid
	os.chown(endfilename, anonyid, -1)


if __name__ == '__main__':

	if raw_input('Type debug to enable debug mode.\n>') == 'debug':
		now = datetime.datetime.now() - datetime.timedelta(days=1)
	else:
		now = datetime.datetime.now()

	todaydate = now.strftime('%d%m%Y')

	mirrortobasnac(todaydate)
