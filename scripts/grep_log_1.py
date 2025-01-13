import re
from collections import defaultdict

# Sample log lines

log_lines = []
with open("/home/aviuser/testing/abc.log", "r") as f:
    for line in f.readlines():
        log_lines.append(line)

# Regex pattern to match models_*
pattern = r"models_\w+\.go:\d{2,5}"

# Dictionary to store types of models_*
models_dict = defaultdict(list)

# Process each log line
for line in log_lines:
    match = re.search(pattern, line)
    if match:
        models_type = match.group()
        models_dict[models_type].append(line)

# Print the types of models_*
for models_type, occurrences in models_dict.items():
    print(f"Type: {models_type}, Occurrences: {len(occurrences)}")
