# pbs_accounting_parser

### Scripts

- parser.py: Parses a pbs accounting file into csv's
- parse_pbs.py: An older version of parser.py that parses a pbs accounting file (does not support parsing of select statements)
- db_writer.py: Takes csv files and writes the contents into a sqlite3 database
- ult_writer.sh: Runs parse_pbs.py and pipes the output csv files into db_writer.py. Also takes in user input and calls create_db.py.
- create_db.py: Creates a sqlite3 database with a set schema for the user

### Instructions to Run

1. Make 3 directories named csv_output, data and logs; parser.py will generate and store logs and csv files in the corresponding directories.

```shell
mkdir csv_output data logs
```

2. Move all the pbs accounting logs into the data directory so the script can access them.


5. Run ult_writer.sh and pass in either the name of the database you want to create or the path to an existing database.

```shell
./ult_writer.sh db_name_here
```
OR
```shell
./ult_writer.sh /path/to/your/database
