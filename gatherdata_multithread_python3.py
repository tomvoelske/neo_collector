#!usr/bin/env python
from sshtunnel import SSHTunnelForwarder
from telnetlib import Telnet
import time
import paramiko
import datetime
import os
import base64
import sys
import threading
import traceback


class Device:

	devicelist = []

	credentialsdict = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
	admindict = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}

	def __init__(self, rawdata):
		rawdatasplit = rawdata.split(' ')

		# getting and assigning raw information

		self.region = rawdatasplit[0]
		self.ip = rawdatasplit[1]
		self.hostname = rawdatasplit[2]
		self.operatingsystem = rawdatasplit[3]
		self.tunnel = rawdatasplit[4]
		self.credentials = rawdatasplit[5]

		# gathers extra information - TODO

		self.extras = []  # TODO: NO EXTRAS PROCESSING YET
		if len(rawdatasplit) > 6:
			for x in range(6, len(rawdatasplit)):
				self.extras.append(rawdatasplit[x])

		self.reportlist = []
		self.errorlist = []

		self.resolve_credentials()

		self.devicelist.append(self)


	def resolve_credentials(self):

		try:
			self.password = base64.b64decode(self.credentialsdict[self.credentials])
			self.adminpassword = base64.b64decode(self.admindict[self.credentials])
			self.valid = True
		except KeyError:
			print('\tERROR: CREDENTIALS NOT FOUND!')
			self.reportlist.append('{0},{1},{2},CREDENTIALS NOT FOUND\r\n'.format(self.region, self.ip, self.hostname))
			self.errorlist.append('{0},{1},{2},CREDENTIALS NOT FOUND\r\n'.format(self.region, self.ip, self.hostname))
			self.valid = False


	def set_backup_loc(self, backupfolder, todaydate):
		self.backuploc = backupfolder + os.sep + self.region + os.sep
		if self.ip != 'ano.nym.ise.dip':
			self.backuploc += self.ip.replace('.', '_') + '.'
			self.connectionname = self.ip
		else:
			self.backuploc += 'ipnotgiven.'
			self.connectionname = self.hostname
		self.backuploc += self.hostname.lower() + '.'
		self.backuploc += todaydate + '.txt'


	def setup(self):

		if not self.valid:
			return

		self.loginobject = [self.credentials, self.password, self.adminpassword, self.hostname]

		if self.operatingsystem == 'ios' or self.operatingsystem == 'catos':

			self.devicethread = threading.Thread(target=ios_catos, args=(self.region, self.operatingsystem,
																		 self.connectionname, self.tunnel,
																		 self.loginobject, self.backuploc, self.reportlist,
																		 self.errorlist))

		else:
			self.valid = False


	def start_gather(self):

		if not self.valid:
			return

		try:
			self.devicethread.start()
		except AttributeError:
			pass


	def finish_gather(self):

		if not self.valid:
			return

		try:
			self.devicethread.join()
		except AttributeError:
			pass


def gather(todaydate, startline=0):

	'''

	:param startline: - line that processing begins from, default 0
	:return: - null

	'''

	# base variables
	rootfolder = '/anonymised/path'
	reportfolder = rootfolder + '/anonymised/path'
	datafolder = rootfolder + '/anonymised/path'
	backupfolder = rootfolder + '/anonymised/path' + os.sep + todaydate

	# creating the backup folder if it doesn't exist
	try:
		os.mkdir(backupfolder)
	except OSError:
		pass

	# file locations
	rawdatasrc = datafolder + '/anonymised/path.txt'
	reportdest = reportfolder + '/' + todaydate + '_gather.txt'
	reportfile = open(reportdest, 'w')
	reportfile.write('REGION,ATTEMPTED CONNECTION NAME,HOSTNAME,LOG\r\n')
	errordest = reportfolder + '/' + todaydate + '_errors.txt'
	errorfile = open(errordest, 'w')
	errorfile.write('REGION,ATTEMPTED CONNECTION NAME,HOSTNAME,LOG\r\n')

	# getting list of devices to back up, main loop
	currentline = startline

	# opening raw data file

	with open(rawdatasrc, 'r') as rawdatafile:

		rawdata = rawdatafile.readlines()

		print('ESTABLISHING COLLECTION OBJECTS\n')

		for i in range(startline, len(rawdata)):
			# looping through the rawdata, from a designated starting line (default = 0 = first line (because index))
			rawdataline = rawdata[i].strip()
			currentline += 1
			if rawdataline and not rawdataline.startswith('#'):

				# creates instance of Device class, also implicity decoding credentials

				device = Device(rawdataline)

				# starting data collection

				print('{0} - {1} ({2}) - {3}/{4}'.format(device.region, device.hostname, device.ip, currentline, len(rawdata)))

				# creates separate region folder, if required

				try:
					os.mkdir(backupfolder + os.sep + device.region)
				except OSError:
					pass

				# defining backup location

				device.set_backup_loc(backupfolder, todaydate)

				# completes initial setup of thread, but does not start running yet

				device.setup()

		print('\n')

	# begins main thread processing, depending on the operating system in use

	print('BEGINNING MAINLINE PROCESSING\n')

	# splits it into chunks to avoid excess memory consumption and silent failures

	n_devices = len(Device.devicelist)
	count = 0

	while count < n_devices:

		chunksize = min(250, n_devices)
		devicechunk = Device.devicelist[count: count + chunksize]
		for device in devicechunk:
			device.start_gather()
		for device in devicechunk:
			device.finish_gather()

		count += chunksize

	# adds reports

	totalreports = []
	totalerrors = []

	for device in Device.devicelist:
		for report in device.reportlist:
			totalreports.append(report)
		for error in device.errorlist:
			totalerrors.append(error)

	for totalreport in sorted(totalreports):
		reportfile.write(totalreport)

	for totalerror in sorted(totalerrors):
		errorfile.write(totalerror)

	# closing files

	reportfile.close()
	errorfile.close()


def ios_catos(region, operatingsystem, connectionname, tunnel, credentials, backuploc, reportlist, errorlist):

	'''

	:param region: - inherited region
	:param operatingsystem: - inherited operating system
	:param connectionname: - inherited connection name - ip preferred, else hostname
	:param tunnel: - telnet or ssh, decides which path it takes
	:param credentials: - credentials in use, a list of 4 items
	:param backuploc: - location of the eventual saved config dump
	:param reportlist: - report list, to pass to addtoreportdata function
	:param errorlist: - error list, to pass to addtoreportdata function
	:return: - null

	'''

	user = credentials[0]
	pw = credentials[1]
	en_pw = credentials[2]
	hostname = credentials[3]

	if tunnel == 'telnet':

		rawexpectedoutput = ['Authentication failed', 'Access denied', 'Invalid input', 'Username:', 'Password:',
							 hostname, hostname + ' [(]enable[)]', hostname + '#', '>']
		expectedoutput = [str.encode('(?i)' + x) for x in rawexpectedoutput]

		try:
			relevant_pw = pw.encode('ascii')
		except AttributeError:
			relevant_pw = pw

		try:
			relevant_en_pw = en_pw.encode('ascii')
		except AttributeError:
			relevant_en_pw = en_pw

		try:
			relevant_user = user.encode('ascii')
		except AttributeError:
			relevant_user = user

		try:
			sock = Telnet(connectionname)
			pwgiven = False

			while True:

				expectresult = sock.expect(expectedoutput, 30)
				if expectresult[0] == -1:
					# misc error
					addtoreportdata(region, connectionname, hostname, 'UNEXPECTED OUTPUT AT LOGIN', reportlist,
									errorlist)
					sock.close()
					return
				elif expectresult[0] <= 2:
					# authentication error
					addtoreportdata(region, connectionname, hostname, 'AUTHENTICATION FAILED', reportlist, errorlist)
					sock.close()
					return
				elif expectresult[0] == 3:
					sock.write(relevant_user + b'\n')
				elif expectresult[0] == 4:
					sock.write(relevant_pw + b'\n')
					pwgiven = True
				elif pwgiven:
					if expectresult[0] != 0:
						break  # escapes loop
					else:
						# authentication error
						addtoreportdata(region, connectionname, hostname, 'AUTHENTICATION FAILED', reportlist, errorlist)
						sock.close()
						return

				time.sleep(1)

			sock.write(b'enable\n')
			sock.read_until(b'Password:', 30)
			sock.write(relevant_en_pw + b'\n')

			expectresult = sock.expect(expectedoutput, 30)

			if expectresult[0] == -1:
				# misc error
				addtoreportdata(region, connectionname, hostname, 'UNEXPECTED OUTPUT WITH ENABLE MODE', reportlist,
								errorlist)
				sock.close()
				return
			elif expectresult[0] <= 1:
				addtoreportdata(region, connectionname, hostname, 'AUTHENTICATION FAILED ENTERING ENABLE MODE', reportlist,
							    errorlist)
				sock.close()
				return
			elif expectresult[0] == 2:
				addtoreportdata(region, connectionname, hostname, 'INVALID INPUT ENTERING ENABLE MODE', reportlist,
								errorlist)
				sock.close()
				return

			sock.write(b'set length 0\n')
			sock.write(b'terminal len 0\n')
			authresult = sock.expect(expectedoutput, 30)

			if authresult[0] == -1:
				# misc error
				addtoreportdata(region, connectionname, hostname, 'UNEXPECTED OUTPUT AFTER ENABLE MODE', reportlist,
							    errorlist)
				sock.close()
				return
			elif authresult[0] == 1:
				addtoreportdata(region, connectionname, hostname, 'AUTHENTICATION FAILED ENTERING ENABLE MODE',
							    reportlist, errorlist)
				sock.close()
				return

			sock.write(b'show run\n')
			time.sleep(1)
			checkrun = sock.read_very_eager()
			if b'Building configuration...' in checkrun:
				# avoids repetition if the prior command worked, but also need to add the captured output
				decodedoutput = checkrun.decode()
			else:
				decodedoutput = ''
				sock.write(b'show running-config\n')
			sock.write(b'echo neo collector done, stage 1/2\n')
			output = sock.read_until(b'neo collector done, stage 1/2', 30)
			sock.write(b'show version\n')
			sock.write(b'echo neo collector done, stage 2/2\n')
			lcmoutput = sock.read_until(b'neo collector done, stage 2/2', 30)

			decodedoutput += output.decode()

			with open(backuploc, 'w') as outputfile:
				outputfile.write('Assumed Operating System: ' + operatingsystem + '\n\n')
				outputfile.write(decodedoutput)
				outputfile.write('\n\n' + '=' * 20 + '\n\n')
				outputfile.write(lcmoutput.decode())
			addtoreportdata(region, connectionname, hostname, 'SUCCESS', reportlist, errorlist, True)
			sock.close()
		except:
			writeerrorlog(hostname, traceback.format_exc())
			addtoreportdata(region, connectionname, hostname, 'MISCELLANEOUS ERROR', reportlist, errorlist)


	elif tunnel == 'ssh':

		try:
			relevant_pw = pw.decode()
		except AttributeError:
			relevant_pw = pw

		try:
			relevant_en_pw = en_pw.decode()
		except AttributeError:
			relevant_en_pw = en_pw

		try:
			relevant_user = user.decode()
		except AttributeError:
			relevant_user = user

		# Create a paramiko ssh client object and load keys.
		# Any missing keys are added to the system.

		sock = paramiko.SSHClient()
		sock.load_system_host_keys()
		sock.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		# Connect to the device using port 22.

		try:
			sock.connect(connectionname, 22, relevant_user, relevant_pw)
		except:
			writeerrorlog(hostname, traceback.format_exc())
			addtoreportdata(region, connectionname, hostname, 'AUTHENTICATION FAILED', reportlist, errorlist)
			sock.close()
			return

		# Cisco devices need to use invoke shell otherwise they
		# drop the connection after 1 command.

		shell = sock.invoke_shell()

		shell.send('enable\n')
		time.sleep(3)
		shell.send(relevant_en_pw + '\n')
		time.sleep(3)
		output = collecttotaloutput(shell)

		if 'Access denied' in output:
			addtoreportdata(region, connectionname, hostname, 'AUTHENTICATION FAILED ENTERING ENABLE MODE',
						    reportlist, errorlist)
			sock.close()
			return
		elif not '(enable)' in output and not '#' in output:
			# misc error
			addtoreportdata(region, connectionname, hostname, 'UNEXPECTED OUTPUT AFTER ENABLE MODE', reportlist,
							errorlist)
			sock.close()
			return

		shell.send('set length 0\n')
		time.sleep(1)
		shell.send('terminal len 0\n')
		time.sleep(1)
		shell.send('show running-config\n')
		time.sleep(5)
		shell.send('show run\n')
		time.sleep(5)
		output = collecttotaloutput(shell)
		shell.send('show version\n')
		time.sleep(5)
		lcmoutput = collecttotaloutput(shell)

		with open(backuploc, 'w') as outputfile:
			outputfile.write(operatingsystem + '\n\n')
			outputfile.write(output)
			outputfile.write('=' * 20 + '\n\n')
			outputfile.write(lcmoutput)
		addtoreportdata(region, connectionname, hostname, 'SUCCESS', reportlist, errorlist, True)
		shell.send('exit\n')
		sock.close()


def collecttotaloutput(datashell):

	output = ''
	starttime = time.time()

	while True:
		if datashell.recv_ready():
			data = datashell.recv(65536).decode('ascii')
			output += data

		if datashell.exit_status_ready():
			break

		# check for timeout
		currenttime = time.time()
		if (currenttime - starttime) > 60:
			break

		if 'neo collector done, stage 2/2' in output:
			break

		time.sleep(0.200)

	if datashell.recv_ready():
		data = datashell.recv(65536)
		output += data.decode('ascii')

	return output


def addtoreportdata(region, connectionname, hostname, errormessage, reportlist, errorlist, success=False):

	'''

	:param region: - inherited region
	:param connectionname: - inherited connection name (ip preferred, else hostname)
	:param hostname: - inherited hostname
	:param errormessage:  - the message given. This is called the errormessage parameter even for a success
	:param report: - report file location
	:param errors: - error file location
	:param success: - if it is a success message, it doesn't write to error file or prefix "ERROR:" to the message
	:return: - null

	'''

	if success:
		print('\t{0} - {1}'.format(hostname, errormessage))
	else:
		print('\t{0} - ERROR: {1}'.format(hostname, errormessage))
		errorlist.append('{0},{1},{2},{3}\r\n'.format(region, connectionname, hostname, errormessage))
	reportlist.append('{0},{1},{2},{3}\r\n'.format(region, connectionname, hostname, errormessage))


def writeerrorlog(hostname, errordata):

	rootfolder = '/anonymised/path/error_logs/'

	with open(rootfolder + hostname + '.txt', 'w') as errorfile:
		errorfile.write(errordata)


if __name__ == '__main__':

	if input('Type debug to enable debug mode.\n>') == 'debug':
		todaydate = datetime.datetime.now() - datetime.timedelta(days=1)
	else:
		todaydate = datetime.datetime.now()

	todaydate = todaydate.strftime('%d%m%Y')

	# processes a designated starting line if valid, else runs with default 0

	if len(sys.argv) > 1:
		try:
			startingline = int(sys.argv[1])
			if startingline < 0:
				print('Argument must be a numeric value > 0.')
				sys.exit(1)
		except ValueError:
			print('Argument must be a numeric value > 0.')
			sys.exit(1)
		gather(todaydate, startingline)
	else:
		gather(todaydate)
