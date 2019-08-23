#!usr/bin/env python
import json


def writejson(jsondata, outputfile):
	jsondump = (json.dumps(jsondata, sort_keys=True, indent=4, separators=(',', ': ')))
	with open(outputfile, 'w') as outfile:
		outfile.write(jsondump)


def readjson(inputfile):
	with open(inputfile, 'r') as infile:
		importedjson = json.load(infile)
		return importedjson


if __name__ == '__main__':
	print('This module must be called from within another.')
