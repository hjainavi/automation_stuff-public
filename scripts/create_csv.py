import json,csv

with open("/home/harsh/optimistic_final_data.json","r") as f:
    config = json.loads(f.read())

for val in config['DATA']:
    loop_count_avg = 0
    time_taken_avg = 0
    file_name = "burst-"+str(val['burst_size'])+"_cooldown-"+str(val['cool_down_interval_secs'])+"_total-"+str(val['total_servers_to_add'])+"_optlock-"+str(val['optimistic_lock'])
    with open("/home/harsh/%s.csv"%(file_name),'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time Stamp","Time Taken","Loop Count"])
        base_time_stamp = int(val['data'][0]['Time Stamp'])
        title = "Burst = %s, Cooldown = %s, Total = %s, Optimistic Lock = %s"%(val['burst_size'],val['cool_down_interval_secs'],val['total_servers_to_add'],val['optimistic_lock'])
        print (title)
        for dat in val['data']:
            writer.writerow([str((int(dat['Time Stamp']) - base_time_stamp)/1000 ),dat['Time Taken'],dat['Loop Count']])

