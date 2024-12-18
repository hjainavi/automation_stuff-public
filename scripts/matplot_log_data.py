import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
from matplotlib.ticker import MultipleLocator
from datetime import datetime


# Sample data
data = []
#pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*\"LLC\sAgent\"\s(\d{1,2}\.\d{3})')
#pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*login\sHTTP.*\s(\d{3})\s.*\"LLC\sAgent\"\s(\d{1,2}\.\d{3})')
#pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*\s(\d{1,2}\.\d{3})\s\d')
pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*\s(\".*\")\s(\d{1,2}\.\d{3})\s\d')
count = 0
agents = set()
with open("/home/aviuser/testing/AV-219088/another_cluster_2/debuglogs.20241021-191222_be2527e6/21_all_logins_all.log", "r") as f:
    for index,line in enumerate(f.readlines()):
        l = re.findall(pattern,line)
        if l:
            if "LLC Agent" in l[0][1]:
                data.append((l[0][0], l[0][1], float(l[0][2])))
                agents.add(l[0][1])
            else:
                data.append((l[0][0], '"Others"', float(l[0][2])))
                agents.add('"Others"')
            '''
            if "Mozilla" in l[0][1] or "Apple" in l[0][1] or "Apple" in l[0][1] or '"-"' in l[0][1]:
                data.append((l[0][0], '"Others"', float(l[0][2])))
                agents.add('"Others"')
            else:
                data.append((l[0][0], l[0][1], float(l[0][2])))
                agents.add(l[0][1])
            '''
            
            
            
#print(agents)
'''
for agent in agents:
    for l in data:
        if agent == l[1]:
            print(l)
            break
'''

# Convert to DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'agent', 'time_taken'])
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%b/%Y:%H:%M:%S')
df['hour'] = df['timestamp'].dt.floor('H')

# Aggregate data
hourly_summary = df.groupby('hour').agg(
    min_time_taken=('time_taken', 'min'),
    avg_time_taken=('time_taken', 'mean'),
    max_time_taken=('time_taken', 'max'),
    total_calls=('time_taken', 'size')
).reset_index()

agent_summary = df.groupby(['hour', 'agent']).size().unstack(fill_value=0).reset_index()

# Plot stacked bar graph for min, avg, max time taken

#fig, ax1 = plt.subplots(figsize=(12, 6))
fig, ax1 = plt.subplots()
fig.set_size_inches(100,50)

bar_width = 0.5
hours = np.arange(len(hourly_summary))
ax1.bar(hours, hourly_summary['min_time_taken'], width=bar_width, label='Min Time Taken', bottom=0)
ax1.bar(hours, hourly_summary['avg_time_taken'] - hourly_summary['min_time_taken'], width=bar_width, label='Avg Time Taken', bottom=hourly_summary['min_time_taken'])
ax1.bar(hours, hourly_summary['max_time_taken'] - hourly_summary['avg_time_taken'], width=bar_width, label='Max Time Taken', bottom=hourly_summary['avg_time_taken'])

ax1.set_xlabel('Hour', fontsize=20)
ax1.set_ylabel('Time Taken (seconds)', fontsize=20)
ax1.yaxis.set_major_locator(MultipleLocator(5))
ax1.set_xticks(hours)
ax1.set_xticklabels(hourly_summary['hour'].dt.strftime('%d/%b/%Y:%H:%M'), rotation=90)
ax1.legend(loc='upper left', prop={'size': 20})

# Line graph for total calls
ax2 = ax1.twinx()
ax2.plot(hours, hourly_summary['total_calls'], color='black', marker='o', label='Total Calls')
ax2.set_ylabel('Total Calls', fontsize=20)
ax2.legend(loc='upper right', prop={'size': 20})

# Add a line for each agent
for agent in agent_summary.columns[1:]:
    ax2.plot(hours, agent_summary[agent], marker='o', label=f'{agent} Calls')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, bbox_to_anchor=(0.5, -0.15), ncol=2, loc='upper right', prop={'size': 20})

# Adjust title size
plt.title('Login API Call Performance Over Time ( debuglogs.20241021-191222_be2527e6 )', fontsize=36)
fig.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("/home/aviuser/debuglogs.20241021-191222_be2527e6_login_calls.jpg")
print("Graph saved")




import sys;sys.exit(0)

# Convert to DataFrame
df = pd.DataFrame(data, columns=['timestamp', 'time_taken'])
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d/%b/%Y:%H:%M:%S')
df['hour'] = df['timestamp'].dt.floor('H')

# Aggregate data
hourly_summary = df.groupby('hour').agg(
    min_time_taken=('time_taken', 'min'),
    avg_time_taken=('time_taken', 'mean'),
    max_time_taken=('time_taken', 'max'),
    total_calls=('time_taken', 'size')
).reset_index()

# Plot
fig, ax1 = plt.subplots()
fig.set_size_inches(50,30)

# Stacked bar graph for min, avg, max time taken
bar_width = 0.5
hours = np.arange(len(hourly_summary))
ax1.bar(hours, hourly_summary['min_time_taken'], width=bar_width, label='Min Time Taken', bottom=0)
ax1.bar(hours, hourly_summary['avg_time_taken'] - hourly_summary['min_time_taken'], width=bar_width, label='Avg Time Taken', bottom=hourly_summary['min_time_taken'])
ax1.bar(hours, hourly_summary['max_time_taken'] - hourly_summary['avg_time_taken'], width=bar_width, label='Max Time Taken', bottom=hourly_summary['avg_time_taken'])


ax1.set_xlabel('Hour', fontsize=20)
ax1.set_ylabel('Time Taken (seconds)', fontsize=20)
ax1.yaxis.set_major_locator(MultipleLocator(5))
ax1.set_xticks(hours)
ax1.set_xticklabels(hourly_summary['hour'].dt.strftime('%d/%b/%Y:%H:%M'), rotation=90)
ax1.legend(loc='upper left', prop={'size': 20})

# Line graph for total calls
ax2 = ax1.twinx()
ax2.plot(hours, hourly_summary['total_calls'], color='black', marker='o', label='Total Calls')
ax2.set_ylabel('Total Calls', fontsize=20)
ax2.legend(loc='upper right', prop={'size': 20})

# Add legends
fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.95])

# Adjust title size
plt.title('Login API Call Performance Over Time ( debuglogs.20240922-224616_15c3a956 )', fontsize=36)

plt.savefig("/home/aviuser/debuglogs.20240922-224616_15c3a956_login_calls.jpg")
print("Graph saved")