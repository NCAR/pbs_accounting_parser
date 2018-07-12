#!/bin/bash

if [ $# -gt 0 ]; then
	if [ -f $1 ]; then
		sed -i '' '71s;.*;		database = "'$1'";' db_writer.py
	else
    	python create_db.py $1
    	sed -i '' '71s;.*;		database = "'$1'";' db_writer.py
    fi
else
    echo "There are no arguments, please provide a database name"
    exit 1
fi



for i in $(ls data/);
do
	python parser.py data/$i 
	csv_files=$(find ./csv_output/* | grep $i)
	python db_writer.py $csv_files 
done
