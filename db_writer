import sqlite3
import csv
from sys import argv

def get_id(connection,table_name,column1,column2):

    c = connection.cursor()

    id_table = {}

    # c.execute('CREATE INDEX {}_index on {} ({})'.format(table_name,table_name,column2))

    for row in c.execute('SELECT {},{} from {}'.format(column1,column2,table_name)):
        id_table[row[1]] = row[0]

    return id_table

def read_csv(file_path):
    with open(file_path, 'rb') as f:
        reader = csv.reader(f)
        return list(reader)


def main():
    if len(argv) < 4:
        print ("jobs resources resource_entries values")
        exit(1)

#Add robust file reading

    else:

        for i in (argv[1:]):
            # print (i)
            if "jobs" in i:
                jobs = read_csv(i)
                continue
            elif "resources" in i:
                resources = read_csv(i)
                continue
            elif "resource_entries" in i:
                r_entries = read_csv(i)
                continue
            elif "resource_entry_values" in i:
                entr_values = read_csv(i)
                continue
        

        conn = sqlite3.connect('db_v3')   # Open a connection to the database
        c = conn.cursor()

        c.executemany('INSERT INTO jobs(id,time,identifier,record) VALUES (?,?,?,?)',jobs)
        conn.commit()

        j_id = get_id(conn,"jobs","job_id","id")   # Pass in connection and return dictionary of id mappings




        for line in resources:
            temp_id = line[0]
            id_to_swap = j_id[int(line[1])]
            resource_var = line[2]
            c.execute('INSERT INTO resources(id,job_id,resource) VALUES (?,?,?)',[temp_id,id_to_swap,resource_var])
        conn.commit()

        r_id = get_id(conn,"resources","primary_id","id")

        

        for row in r_entries:
            auto_id = row[0]
            swap_id = r_id[int(row[1])]
            value = row[2]
            c.execute('INSERT INTO resource_entries(id,resource_id,value) VALUES (?,?,?)',[auto_id,swap_id,value])
        conn.commit()

        e_id = get_id(conn,"resource_entries","primary_id","id")

        

        for loin in entr_values:
            new_id = e_id[int(loin[0])]
            val = loin[1]
            c.execute('INSERT INTO rentry_values(re_id,key) VALUES (?,?)',[new_id,val])
        conn.commit()

        conn.execute("VACUUM")

if __name__ == "__main__":
	main()
