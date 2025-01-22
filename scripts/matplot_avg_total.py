import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re, sys, time
# Sample data
pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*"\s(\d{1,2}\.\d{3})')
#pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*login\sHTTP.*\s(\d{3})\s.*\"LLC\sAgent\"\s(\d{1,2}\.\d{3})')
count = 0
timestamps = []
times = []
print(datetime.now())
with open("/home/aviuser/testing/AV-227548/debuglogs.20250113-150728_e5a55fdc/nginx_all.log", "r") as f:
    for line in f.readlines():
        l = re.findall(pattern,line)
        if l and ("Dec" in l[0][0] or "Jan" in l[0][0]) and "2024" in l[0][0]: 
            timestamps.append(datetime.strptime(l[0][0], '%d/%b/%Y:%H:%M:%S'))
            times.append(float(l[0][1]))


print(datetime.now())
# Create a DataFrame
df = pd.DataFrame({'timestamp': timestamps, 'time_taken': times})
df['hour'] = df['timestamp'].dt.floor('H')

print(datetime.now())
# Group by hour and calculate min, mean, max
grouped = df.groupby('hour')['time_taken'].agg(['min', 'mean', 'max'])

print(datetime.now())
# Plot the stacked bar graph
grouped.plot(kind='bar', stacked=True, figsize=(200, 120), color=['#1f77b4', '#ff7f0e', '#2ca02c'])
plt.xlabel('Hourly Timestamp')
plt.ylabel('Time Taken (s)')
plt.title('Min, Average, and Max Time Taken for API Calls Over an Hour')
plt.xticks(rotation=45)
plt.legend(['Min Time', 'Average Time', 'Max Time'])
print(datetime.now())
plt.show()
print(datetime.now())
# Save the plot
plt.savefig("/home/aviuser/hourly_call_count.jpg")
print(datetime.now())
print("Graph saved as /home/aviuser/hourly_call_count.jpg")
print(datetime.now())
# Display the plot (uncomment if running in an interactive environment)
# plt.show()