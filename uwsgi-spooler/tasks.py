from uwsgidecorators import spool
import time
import sqlite3
from sqlite3 import Error
import os
import time
#from uwsgi_tasks import get_current_task

db_filename = '/home/aviuser/uwsgi-spooler/stats.db' 

db_exists = os.path.exists(db_filename)

with sqlite3.connect(db_filename) as conn:
    if not db_exists:
        print('Creating schema')
        conn.execute("""
        create table table_demo (
            id  integer primary key autoincrement not null,
            name text,
            time real
            )""")

    else:
        print('DB already exists.')



@spool
def a_long_task(args):
    #with open("abc.txt","a") as f:
    #    f.write(args)
    with sqlite3.connect(db_filename) as conn:
        cur = conn.cursor()
        cur.execute("""
        insert into table_demo (name,time) values ('%s',%s);
        """%(args['foo'],args['time']))
    #print args
    #args['ud_spool_ret']='-1'
    

    with sqlite3.connect(db_filename) as conn2:
        c = conn2.cursor()
        c.execute('select * from table_demo')
        print c.fetchall()

