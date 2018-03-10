from sys import argv,exit
from string import split,join
import csv
import os
import time
import calendar
import re

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

def parse_select(val):
	print val
	squote = 0
	dquote = 0
	paren = 0
	key = ""
	value = ""
	in_key = 1
	copies = 0
	listoflists = []
	rlist = []
	temp = {}

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
					# rlist.append("copies:"+value)
					listoflists.append("copies:"+value)
					# rval["copies"] = value
				else:
					rlist.append(key+":"+value)
					# rval[key] = value  # If important semicolon then it is separating a key from a value so write what we have in and then start on the new key

				key = ""
				value = ""
				continue

		# Plus signs = extra chunks
		if val[i] == '+':
			if in_key==0 and (squote > 0 or dquote > 0 or paren > 0):
				value+=val[i]
			elif in_key==0 and (squote == 0 or dquote == 0 or paren == 0):
				rlist.append(key+":"+value)
				listoflists.append(rlist)
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
		listoflists.append(rlist)
		# rval["invalid"] = value
	else:
		rlist.append(key+":"+value)
		listoflists.append(rlist)
		# rval[key] = value

	print listoflists
	# print rval
	return rlist




def main():
	do_output = 0
	if len(argv) < 3:
		print "accounting_file [key_table] [job_table]"
		exit(1)
	if len(argv) > 2:
		do_output = 1
		key_table_fd = open(argv[2], 'w')
		key_table = csv.writer(key_table_fd)

		record_table_fd = open(argv[3], 'w')
		record_table = csv.writer(record_table_fd)

		res_table_fd= open('resource_type','w')
		res_table = csv.writer(res_table_fd)

	accounting_file = open(argv[1], 'r')

	accounting_file_name = os.path.basename(argv[1])

	record_id = -1
	for entry in accounting_file:
		record_id = record_id + 1
		fields = split(entry, ';')
		rtime = time.strptime(fields[0], "%m/%d/%Y %H:%M:%S") #localtime() -- local time
		rtime = calendar.timegm(rtime)
		etype = fields[1] #[LQSED]
		entity = fields[2] #"license" or job number
		message = join(fields[3:])
		if etype == 'L':
			continue #PBS license stats? not associated with a job
		rec = parse_acct_record(message)


		keystr = [accounting_file_name, record_id, rtime, entity]
		if do_output == 1:
			record_table.writerow(keystr + [etype])
			for k,v in rec.iteritems():

				res_table.writerow([k])

				if re.search("select",k):
					result = parse_select("="+v)
					# print result

					# for s_key, val in result.iteritems():
						# key_table.writerow(keystr + [k, s_key,val])

					for i in result:
						key_table.writerow(keystr + [k,i])
				else:
					key_table.writerow(keystr + [k, v] )
		if do_output == 0:
			print rec

	if do_output == 1:
		key_table_fd.close()
		record_table_fd.close()

	accounting_file.close()


if __name__ == "__main__":
	main()
