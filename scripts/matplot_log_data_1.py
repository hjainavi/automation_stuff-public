import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import re

# Sample data
data = []
pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*"\s(\d{1,2}\.\d{3})')

with open("/home/aviuser/testing/AV-227548/debuglogs.20250113-150728_e5a55fdc/nginx_all.log", "r") as f:
    for line in f.readlines():
        l = re.findall(pattern,line)
        if l and ("Dec" in l[0][0] or "Jan" in l[0][0]) and "2024" in l[0][0]: 
            data.append((datetime.strptime(l[0][0], '%d/%b/%Y:%H:%M:%S'), float(l[0][1])))


# Convert data to DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'time_taken'])
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%b/%Y:%H:%M:%S')

# Set the interval to 20 minutes
df.set_index('timestamp', inplace=True)
df_resampled = df.resample('20T').agg({'time_taken': ['min', 'max', 'mean'], 'time_taken': 'count'})
df_resampled.columns = ['min_time_taken', 'max_time_taken', 'avg_time_taken', 'count']

# Plotting
fig, ax1 = plt.subplots()

# Bar graph for min, max, and avg time taken
ax1.bar(df_resampled.index, df_resampled['min_time_taken'], width=0.01, label='Min Time Taken', color='b', alpha=0.7)
ax1.bar(df_resampled.index, df_resampled['max_time_taken'], width=0.01, label='Max Time Taken', color='r', alpha=0.7)
ax1.bar(df_resampled.index, df_resampled['avg_time_taken'], width=0.01, label='Avg Time Taken', color='g', alpha=0.7)

ax1.set_xlabel('Time (20-minute intervals)')
ax1.set_ylabel('Time Taken')
ax1.legend(loc='upper left')

# Line graph for total number of entries
ax2 = ax1.twinx()
ax2.plot(df_resampled.index, df_resampled['count'], label='Total Entries', color='k', linestyle='-', marker='o')
ax2.set_ylabel('Total Entries')
ax2.legend(loc='upper right')

fig.tight_layout()

plt.savefig("/home/aviuser/hourly_call_count.jpg")
print("Graph saved")
