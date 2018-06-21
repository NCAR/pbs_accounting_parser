#!/bin/bash -x

for i in $(ls data/);
do
	python parser.py data/$i 
	csv_files=$(find ./csv_output/* | grep $i)
	python db_writer.py $csv_files 
done
