from sys import argv,exit,stdout
from string import split,join
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
	rval[key] = value
	return rval


def main():
	if len(argv) < 2:
		exit(1)

	accounting_file = open(argv[1], 'r')

	for entry in accounting_file:
		fields = split(entry, ';')
		time = fields[0] #localtime() -- local time
		etype = fields[1] #[LQSED]
		entity = fields[2] #"license" or job number	
		message = join(fields[3:])
		if etype == 'L':
			continue #PBS license stats? not associated with a job
		if entity.find(argv[2]) is not -1:
			rec = parse_acct_record(message)
			if "exec_host" in rec:
				print entity
				for n in re.findall("(r)([0-9]+)(i)([0-9]+)(n)([0-9]+)", rec["exec_host"]):
					stdout.write("%s," % ("".join(n),))
				print ""

	accounting_file.close()


if __name__ == "__main__":
	main()
