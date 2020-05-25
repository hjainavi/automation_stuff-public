import re , os
from datetime import datetime
from peewee import *

file_paths = []
for root,dirs,files in os.walk("/root/testing/AV-85198/debuglogs.20200516-233545"):
    for f in files:
        if "aviportal.log" in f and "prev" not in root and ".swp" not in f:
            file_paths.append(os.path.join(root,f))

db = SqliteDatabase('pool_database.db')

class BaseModel(Model):
    class Meta:
        database = db

class Pool_Logs(BaseModel):
    pool_uuid = CharField()
    timestamp = DateTimeField()
    time_taken = IntegerField() # in msecs
    response_code = IntegerField()


db.connect()
db.create_tables([Pool_Logs])


pattern = re.compile('(\[\w{2,4} ([\w :]+)\] PATCH /api/pool/([\w -]+) .*generated \d{1,5} bytes in (\d{2,8}) msecs \(HTTP/1.1 (\d{1,5}).*\n)')

data_source = []

for path in file_paths:
    with open(path,'r') as f:
        logs = f.read()
        res = re.findall(pattern, logs)
        if res:
            total_length = len(res)
            for index,val in enumerate(res):
                _ , datetime_str , pool_uuid , time_taken , response_code = val
                datetime_sql_non = datetime.strptime(datetime_str, "%b %d %H:%M:%S %Y")
                datetime_sql = datetime_sql_non.strftime("%Y-%m-%d %H:%M:%S")
                data_source.append({'pool_uuid':pool_uuid, 'timestamp':datetime_sql, 'time_taken':time_taken, 'response_code':response_code})
                if index % 100 == 0 or index == total_length-1:
                    with db.atomic():
                        Pool_Logs.insert_many(data_source).execute()
                    data_source = []

cursor = db.execute_sql('select count(*) from Pool_Logs;')
res = cursor.fetchone()
print('Total: ', res[0])                    

cursor = db.execute_sql("select time_taken , CAST(strftime('%s',timestamp) AS INT) as tt from pool_logs where response_code = 200 and pool_uuid='pool-1bf5e3ac-54e9-400c-b0b4-b1c8a2e3a085' order by tt;")  
res = cursor.fetchall()
timetaken_timestamp = []
dup = {}
for i in res:
    if dup.get(i[1],False):
        pass
    else:
        timetaken_timestamp.append([i[0],i[1]])

import csv
with open('employee_file.csv', mode='w') as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for i in timetaken_timestamp:
        employee_writer.writerow(i)
