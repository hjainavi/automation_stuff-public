import re
from datetime import datetime, timedelta

entry = "drwxr-xr-x 2 root root 4096 2024-12-21 21:07:06 3645615744"

# Regex pattern to match the timestamp
timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"

# Search for the timestamp in the entry
match = re.search(timestamp_pattern, entry)

if match:
    timestamp = match.group()
    print("Timestamp:", timestamp)
else:
    print("Timestamp not found.")

# Convert the string to a datetime object
timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")

# Subtract ten minutes
new_timestamp_dt = timestamp_dt - timedelta(minutes=10)

# Convert the datetime object back to a string
new_timestamp = new_timestamp_dt.strftime("%Y%m%d%H%M.%S")

print("New Timestamp:", new_timestamp)
