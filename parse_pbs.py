#MIT License
#
#Copyright (c) 2018 National Center for Atmospheric Research
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


from sys import argv,exit
from string import split,join
import csv
import os
import time
import calendar

def parse_acct_record(m):
	squote = 0
	dquote = 0
	paren = 0
	key = ""
	value = ""
	in_key = 1
	rval = {}

	for i in range(0, len(m)):
		#safety checks
		if in_key < 0:
			raise Exception("Unexpected Happened")
		if in_key < 1 and key == "":
			raise Exception("Null Key")

		#parens seem to be super-quotes
		if m[i] == '(':
			paren = paren + 1
		if m[i] == ')':
			paren = paren - 1	
		#single quotes are the next strongest escape character
		if m[i] == '\'':
			if squote > 0:
				squote = squote - 1
			else:
				if dquote > 1:
					raise Exception("Don't think this can happen")
				squote = squote + 1
		#then double quotes
		if m[i] == '"':
			if dquote > 0 and squote == 0:
				dquote = dquote - 1
			else:
				dquote = dquote + 1
		#last, equal signs
		if m[i] == '=' and squote == 0 and dquote == 0 and paren == 0:
			if value is "":
				in_key = 0
				continue
			else:
				if not (m[i] == '=' and in_key == 0):
					#pretty sure you can't have an equal in a key
					print m
					raise Exception("Unhandled Input", m[i])
		if m[i] == ' ' and (squote > 0 or dquote > 0 or paren > 0):
			if in_key == 1:
				key += m[i]
				continue
			else:
				value += m[i]
				continue
		if m[i] == ' ' and in_key==0:
			#print "Key: " + key
			#print "Value: " + value
			if not key in rval:
				rval[key] = value
			else:
				raise Exception("Duplicate Key")
			in_key = 1
			key = ""
			value = ""
			continue
		if m[i] == ' ':
			continue
			raise Exception("Unexpected whitespace")
		if in_key == 1:
			key += m[i]
		if in_key == 0:
			value += m[i]
	if in_key == 1 and len(key) > 1:
		#raise Exception("Partial Record Detected", argv[1])
		print "Warning: Gibberish: " + key
	rval[key.rstrip('\n')] = value.rstrip('\n')
	return rval

def main():
	do_output = 0
	if len(argv) < 2:
		print "accounting_file [key_table] [job_table]"
		exit(1)
	if len(argv) > 2:
		do_output = 1
		key_table_fd = open(argv[2], 'w')
		key_table = csv.writer(key_table_fd)
		record_table_fd = open(argv[3], 'w')
		record_table = csv.writer(record_table_fd)

	accounting_file = open(argv[1], 'r')

	accounting_file_name = os.path.basename(argv[1])


	for entry in accounting_file:
		fields = split(entry, ';')
		rtime = time.strptime(fields[0], "%m/%d/%Y %H:%M:%S") #localtime() -- local time
		rtime = calendar.timegm(rtime)
		etype = fields[1] #[LQSED]
		entity = fields[2] #"license" or job number	
		message = join(fields[3:])
		if etype == 'L':
			continue #PBS license stats? not associated with a job
		rec = parse_acct_record(message)

		keystr = [accounting_file_name, rtime, entity]
		if do_output == 1:
			record_table.writerow(keystr + [etype])
			for k,v in rec.iteritems():
				print k,v
				key_table.writerow(keystr + [k, v] )
		if do_output == 0:
			print rec
	if do_output == 1:
		key_table_fd.close()
		record_table_fd.close()

	accounting_file.close()


if __name__ == "__main__":
	main()
