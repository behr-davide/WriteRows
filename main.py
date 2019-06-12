import os
import pyodbc
import csv
import sys
from tqdm import tqdm
import argparse

# workaround for ascii encoding error
reload(sys)
sys.setdefaultencoding('utf8')

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise ValueError(string, ' is not a valid directory')

parser = argparse.ArgumentParser()
parser.add_argument("server", help="enter the name of the server")
parser.add_argument("database", help="enter the name of the database")
parser.add_argument("rtf_table", help="enter the name of table containing rtf data")
parser.add_argument("output_directory", help="enter the name of the output directory", type=dir_path)
args = parser.parse_args() 

class Connection(object):
    def __init__(self, connection_string):
        self.con = pyodbc.connect(connection_string)
        self.cur = self.con.cursor()

    def __del__(self):
        self.cur.close()
        print("cursor closed")
        self.con.close()
        print("connection closed")

    def commit(self):
        self.con.commit()

    def execute(self, query):
        try:
            query_results = self.cur.execute(query)
        except pyodbc.Error as e:
            sqlerror = e.args[1]
            print(str(sqlerror))
        return query_results

    def get_records(self, file_query):
        qr = self.execute(file_query).fetchall()
        return qr

    def get_count(self, count_query):
        total_records = self.execute(count_query).fetchval()
        return total_records

    @staticmethod
    def write_records(results, conversion_dir, total_records):
        os.chdir(conversion_dir)
        error_list = []
        # powershell freaks out w/o ascii progress bar
        for row in tqdm(results, total=total_records, ascii=True):
            try:
                with open(r'{0}.rtf'.format(row[0]), "w") as f:
                    f.write(str(row[1]))
            except Exception as e:
                error_list.append((row[0], e))
        return error_list


def log_errors(error_list):
    '''display errors, in shell and in local file'''
    if not error_list:
        print('No Errors')
        return
    open_file = open('error_log.txt', 'w')
    for file_id, error in error_list:
        open_file.write('Unique ID - ' + str(file_id) + '\n')
        open_file.write('Error - ' + str(error) + '\n')


def main():
    # use windows auth
    connection_string = r'Driver={SQL Server};Server={0};Database={1};Trusted_Connection=yes;'.format(args.server, args.database)
    conversion_dir = args.output_directory
    fqSQL = r'SELECT * FROM {0};'.format(args.rtf_table)
    cqSQL = r'SELECT COUNT(*) FROM {0};'.format(args.rtf_table)  

    write_cnxn = Connection(connection_string)
    res = write_cnxn.get_records(fqSQL)
    count = write_cnxn.get_count(cqSQL)
    errors = write_cnxn.write_records(res, conversion_dir, count)
    log_errors(errors)


if __name__ == "__main__":
    main()
