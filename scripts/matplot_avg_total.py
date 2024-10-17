import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re, sys
# Sample data
log_data = []
pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*\"LLC\sAgent\"\s(\d{1,2}\.\d{3})')
#pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*login\sHTTP.*\s(\d{3})\s.*\"LLC\sAgent\"\s(\d{1,2}\.\d{3})')
count = 0
with open("/home/aviuser/testing/AV-219088/debuglogs.20240926-035202_b88eae05/26_all_logins.log", "r") as f:
    for line in f.readlines():
        l = re.findall(pattern,line)
        if l: 
            log_data.append(l[0])
            print(l[0])



# Parse the log data
timestamps = [datetime.strptime(entry[0], '%d/%b/%Y:%H:%M:%S') for entry in log_data]
times = [float(entry[1]) for entry in log_data]

# Create a DataFrame
df = pd.DataFrame({'timestamp': timestamps, 'time_taken': times})
df['hour'] = df['timestamp'].dt.floor('H')

# Group by hour and calculate min, mean, max
grouped = df.groupby('hour')['time_taken'].agg(['min', 'mean', 'max'])

# Plot the stacked bar graph
grouped.plot(kind='bar', stacked=True, figsize=(50, 60), color=['#1f77b4', '#ff7f0e', '#2ca02c'])
plt.xlabel('Hourly Timestamp')
plt.ylabel('Time Taken (s)')
plt.title('Min, Average, and Max Time Taken for API Calls Over an Hour')
plt.xticks(rotation=45)
plt.legend(['Min Time', 'Average Time', 'Max Time'])
plt.show()
# Save the plot
plt.savefig("/home/aviuser/hourly_call_count.jpg")
print("Graph saved as 'hourly_call_count.png'")

# Display the plot (uncomment if running in an interactive environment)
# plt.show()
