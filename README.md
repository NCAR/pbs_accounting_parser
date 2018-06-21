# pbs_accounting_parser

### Scripts

- parse_pbs.py: Parses a pbs accounting file into csv's
- db_writer.py: Takes csv files and writes the contents into a sqlite3 database
- ult_writer.sh: Runs parse_pbs.py and pipes the output csv files into db_writer.py

### Instructions to Run

1. Make 3 directories named csv_output, data and logs
2. Throw all the pbs accounting logs into the data directory
3. Create a sqlite database
4. Edit the db_writer.py file by adding in the name of your database on line 49
5. Run ult_writer.sh

