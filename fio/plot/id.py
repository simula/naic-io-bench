import sys
import os
import json
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from cycler import cycler

# Dirs
IMG_DIR = "/mnt/c/Users/Public/Public Code/naic-io-bench/fio/img"
DATA_DIR = "/mnt/c/Users/Public/Public Code/naic-io-bench/fio/out"

# Plot title and axis labels
TITLE = 'Throughput vs. IO Depth (Sequential Write)'
# TITLE = 'Throughput vs. IO Depth (Random Write)'
# TITLE = 'Throughput vs. IO Depth'
X_LABEL = 'IO Depth'
Y_LABEL = 'Throughput (MB/s)'

# Plot dimensions
HEIGHT = 6
WIDTH = 8

# Plot settings
X_SCALE = 'linear'
Y_SCALE = 'linear'

# Labels (legend)
LABELS = [
    'IPoPCIe',
    'Ethernet',
    # 'IPoPCIe (Sequential)',
    # 'Ethernet (Sequential)',
    # 'IPoPCIe (Random)',
    # 'Ethernet (Random)',
]

# Custom colors
custom_colors = [
    "#389e9b",  # Dolphin
    "#fab900",  # BeeGFS
    "#dd0001",  # UiO
    "#df47be",  # Pink
]

plt.rcParams['axes.prop_cycle'] = cycler(color=custom_colors)

# Command line arguments
if len(sys.argv) < 3:
    exit('Usage: python tp_vs_id.py <out_file_name> <job1> [<job2> ...]')

out_file_name = sys.argv[1]
jobs = sys.argv[2:]
num_jobs = len(jobs)

# Create the plot.
plt.figure(figsize=(WIDTH, HEIGHT))

# Loop over each job name.
for i, job in enumerate(jobs):
    input_path = os.path.join(DATA_DIR, job)
    
    # Load the JSON data.
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    iodepths = []
    throughputs = []
    
    # Process each job entry in the JSON.
    for sub_job in data.get('jobs', []):
        # Retrieve the iodepth from the job options.
        iodepth_str = sub_job.get('job options', {}).get('iodepth', None)
        if iodepth_str is None:
            continue
        try:
            # Convert iodepth to a float (or int).
            iodepth_val = float(iodepth_str)
        except ValueError:
            continue
        iodepths.append(iodepth_val)
        
        # Retrieve the write bandwidth in KB/s, then convert to MB/s.
        bw_kb = sub_job.get('write', {}).get('bw', 0)
        bw_mb = bw_kb / 1024.0
        throughputs.append(bw_mb)
    
    # If valid data was found, sort by IO depth and plot.
    if iodepths and throughputs:
        sorted_data = sorted(zip(iodepths, throughputs))
        iodepths, throughputs = zip(*sorted_data)
        plt.plot(iodepths, throughputs, marker='o', linestyle='-', label=LABELS[i])
    else:
        print(f'No valid data found in {input_path}')



plt.style.use('seaborn-v0_8-paper')
ax = plt.gca()  # Get current axes
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.xlabel(X_LABEL)
plt.ylabel(Y_LABEL)
plt.title(TITLE)
plt.grid(True)
plt.xscale(X_SCALE)
plt.yscale(Y_SCALE)

if num_jobs > 1: (plt.legend())

# Save the plot to the designated output path.
output_path = os.path.join(IMG_DIR, out_file_name)
plt.savefig(output_path, dpi=300)

