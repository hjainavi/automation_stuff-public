import re, json
from datetime import datetime

with open("/root/optimistic_lock.log","r") as f:
    config = f.read()
    pattern = re.compile('\[(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d,\d\d\d)\].*\nREQUEST (\d{1,4}) :: Loop count : (\d{1,4}) ; Time spent to pass : (\d{1,3}\.\d{1,3}) ; Final status code : (\d{3}) ; Unique ID : ([a-zA-Z0-9-]*)')
    #time_stamp, request_no , loop_count , time_taken , status_code , id
    res = re.findall(pattern,config)

# data from requests file from dev machine
with open("/root/optimistic_request_file.json" , "r") as f:
    config = json.loads(f.read())['request_data']
new_data = []
for req in config:
    temp = []
    avg_loop_count = 0
    avg_time_taken = 0
    sum_loop = 0
    sum_time = 0 
    for data in res:
        if req['id'] == data[5]:
            epoch = datetime.utcfromtimestamp(0)
            dt = datetime.strptime(data[0],'%Y-%m-%d %H:%M:%S,%f')
            val = (dt - epoch).total_seconds() * 1000
            temp.append({'Time Stamp Relative':val, 'Request No':data[1], 'Loop Count':data[2], 'Time Taken':data[3], 'Status Code':data[4], "Timestamp original":data[0]})
            sum_loop += data[2]
            sum_time += data[3]
    req['Avg Time Taken'] = sum_time/len(temp)
    req['Avg Loop Count'] = sum_loop/len(temp)
    req['data'] = temp
    new_data.append(req)
print new_data

with open("/root/optimistic_final_data.json" , "w") as f:
    final_data = {'DATA':new_data}
    json.dump(final_data, f, indent=4)

