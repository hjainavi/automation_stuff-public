
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


# Extract timestamps from log data
timestamps = []
pattern = re.compile(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})')
with open("/home/aviuser/all_27_nginx_login.log", "r") as f:
    for line in f.readlines():
        l = re.findall(pattern, line)
        if l: timestamps.extend(l)

# Convert timestamps to datetime objects
dates = [datetime.strptime(ts, '%d/%b/%Y:%H:%M:%S') for ts in timestamps]

# Create a DataFrame
df = pd.DataFrame(dates, columns=['datetime'])

# Set the datetime column as the index
df.set_index('datetime', inplace=True)

# Resample to hourly frequency and count logins
hourly_logins = df.resample('H').size()

# Plot the data
plt.figure(figsize=(30, 20))
hourly_logins.plot(kind='bar')
plt.title('Logins Per Hour')
plt.xlabel('Hour')
plt.ylabel('Number of Logins')
plt.savefig("/home/aviuser/27_log_image")
