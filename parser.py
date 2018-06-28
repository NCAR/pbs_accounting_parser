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
import re

def parse_acct_record(m,filename):
	squote = 0
	dquote = 0
	paren = 0
	key = ""
	value = ""
	in_key = 1
	rval = {}

	logfile = open('logs/log_'+filename,'w')

	for i in range(0, len(m)):
		#safety checks
		if in_key < 0:
			logfile.write("WARNING: in_key variable set to invalid number")
		if in_key < 1 and key == "":
			logfile.write("WARNING: Null key")

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
					# print m
					logfile.write("WARNING: Unhandled Input")
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
				logfile.write("WARNING: Duplicate key, could affect the data that's parsed. Key: {} Value: {}".format(key,value))
			in_key = 1
			key = ""
			value = ""
			continue
		if m[i] == ' ':
			continue
			logfile.write("Unexpected Whitespace")
		if in_key == 1:
			key += m[i]
		if in_key == 0:
			value += m[i]
	if in_key == 1 and len(key) > 1:
		#raise Exception("Partial Record Detected", argv[1])
		logfile.write("Warning: Gibberish: " + key)
	rval[key.rstrip('\n')] = value.rstrip('\n')
	return rval

def parse_select(val):
	# print val
	squote,dquote,paren,copies = 0,0,0,0
	key = ""
	value = ""
	in_key = 1
	listoflists = []
	rlist = []

	for i in range(0,len(val)):

		#Parentheses
		if val[i] == '(':
			squote+=1
		if val[i] == ')':
			squote-=1

		#Single Quote
		if val[i] == '\'':
			if squote > 0:
				squote-=1

		#Double Quotes
		if val[i] == '"':
			if dquote > 0:
				dquote-=1
			else:
				dquote+=1

		# Semicolon
		if val[i] == ':':
			if in_key==0 and (squote > 0 or dquote > 0 or paren > 0):
				value+=val[i]  #If theres still a grouping operator just assume its a part of the value
				continue
			elif in_key==0 and (squote == 0 and dquote == 0 and paren == 0):
				in_key = 1

				if key == "" and value.isdigit():
					# listoflists.append(value)
					copies = value

				else:
					rlist.append(key+":"+value)

				key = ""
				value = ""
				continue

		# Plus signs = extra chunks
		if val[i] == '+':
			if in_key==0 and (squote > 0 or dquote > 0 or paren > 0):
				value+=val[i]
			elif in_key==0 and (squote == 0 or dquote == 0 or paren == 0):
				rlist.append(key+':'+value)
				listoflists.append(tuple([copies,rlist]))
				rlist = []
				key = ""
				value = ""
			continue

		# Equals
		if val[i] == '=' and (squote == 0 and dquote == 0 and paren == 0):
			if value is "":
				in_key = 0
				continue
		if val[i] == ' ' and (squote > 0 or dquote > 0 or paren > 0):
			if in_key == 1:
				key += val[i]
				continue
			else:
				value += val[i]
				continue

		if in_key == 1:
			key += val[i]
		if in_key == 0:
			value += val[i]

	if key== "":
		rlist.append("invalid:"+value)
		listoflists.append(tuple([copies,rlist]))

	else:
		rlist.append(key+":"+value)
		listoflists.append(tuple([copies,rlist]))


	# print listoflists
	return listoflists




def main():
	do_output = 0
	if len(argv) < 2:
		print "accounting_file"
		exit(1)
	else:
		do_output = 1
		name_str = '_'+(argv[1].split('/')[1])

		resource_table_fd = open('csv_output/resources' + name_str, 'w')
		resource_table = csv.writer(resource_table_fd)

		jobs_table_fd = open('csv_output/jobs'+ name_str, 'w')
		jobs_table = csv.writer(jobs_table_fd)

		entries_table_fd= open('csv_output/resource_entries'+ name_str,'w')
		entries_table = csv.writer(entries_table_fd)

		values_table_fd = open('csv_output/resource_entry_values'+ name_str,'w')
		values_table = csv.writer(values_table_fd)

		accounting_file = open(argv[1], 'r')

		accounting_file_name = os.path.basename(argv[1])

	job_id = -1
	resource_id = -1
	entry_id = -1

	for entry in accounting_file:
		job_id = job_id + 1
		fields = split(entry, ';')
		rtime = time.strptime(fields[0], "%m/%d/%Y %H:%M:%S") #localtime() -- local time
		rtime = calendar.timegm(rtime)
		etype = fields[1] #[LQSED]
		entity = fields[2] #"license" or job number
		message = join(fields[3:])
		if etype == 'L':
			continue #PBS license stats? not associated with a job, skip

		rec = parse_acct_record(message,accounting_file_name)

		keystr = [job_id , rtime, entity]

		if do_output == 1:
			jobs_table.writerow(keystr + [etype])   #Writes jobs csv file

			for k,v in rec.iteritems():

				resource_id+=1
				entry_id+=1
				keystr1 = [resource_id,job_id]

				if re.search("select",k):
					resource_table.writerow(keystr1 + [k])

					result = parse_select("="+v)
					# tuple[0] goes in entries table, tuple[1] is delimited by ':' and goes into values table
					for tup in result:
						entry_id+=1
						entries_table.writerow([entry_id,resource_id] + [tup[0]])
						for val in tup[1]:
							values_table.writerow([entry_id] + [val])

				else:
					resource_table.writerow(keystr1 + [k])
					entries_table.writerow([entry_id,resource_id] + [v])
		if do_output == 0:
			print rec

	if do_output == 1:
		resource_table_fd.close()
		jobs_table_fd.close()
		entries_table_fd.close()
		values_table_fd.close()

	accounting_file.close()


if __name__ == "__main__":
	main()
