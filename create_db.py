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

import sqlite3
from sys import argv

database = argv[1]

conn = sqlite3.connect(database)
c = conn.cursor()

c.execute('CREATE TABLE jobs(job_id integer primary key autoincrement,id integer,time integer,identifier varchar(255),record text,CONSTRAINT job_unique UNIQUE (time, identifier, record));')

c.execute('CREATE TABLE resources(primary_id integer primary key autoincrement,id integer,job_id integer,resource varchar(255));')

c.execute('CREATE TABLE resource_entries(primary_id integer primary key autoincrement,id integer,resource_id integer,value varchar(255));')

c.execute('CREATE TABLE rentry_values(re_id integer,key varchar(255));')

conn.close()