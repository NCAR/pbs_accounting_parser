# pbs_accounting_parser

### Scripts

- parser.py: Parses a pbs accounting file into csv's
- parse_pbs.py: An older version of parser.py that parses a pbs accounting file (does not support parsing of select statements)
- db_writer.py: Takes csv files and writes the contents into a sqlite3 database
- ult_writer.sh: Runs parse_pbs.py and pipes the output csv files into db_writer.py

### Instructions to Run

1. Make 3 directories named csv_output, data and logs; parser.py will generate and store logs and csv files in the corresponding directories.

```shell
mkdir csv_output data logs
```

2. Move all the pbs accounting logs into the data directory
3. Create a sqlite database with the following schema

```sql
CREATE TABLE jobs(
job_id integer primary key autoincrement,
id integer,
time integer,
identifier varchar(255),
record text,
CONSTRAINT job_unique UNIQUE (time, identifier, record)
);

CREATE TABLE resources(
primary_id integer primary key autoincrement,
id integer,
job_id integer,
resource varchar(255)
);

CREATE TABLE resource_entries(
primary_id integer primary key autoincrement,
id integer,
resource_id integer,
value varchar(255)
);

CREATE TABLE rentry_values(
re_id integer,
key varchar(255)
);
```

4. Edit the db_writer.py file by adding in the name of your database on line 72

```python
conn = sqlite3.connect('your_db_name_here')
```

5. Run ult_writer.sh
