import sys
import os
import json
import argparse
import matplotlib.pyplot as plt
from cycler import cycler

# Dirs
IMG_DIR = "/mnt/c/Users/Public/Public Code/naic-io-bench/fio/img"
DATA_DIR = "/mnt/c/Users/Public/Public Code/naic-io-bench/fio/data"

# Custom colors
palette = {
    "eth":    "#FAB900",  # BeeGFS
    "eth2":   "#FFC92E",  # BeeGFS light
    "dis":    "#389E9B",  # Dolphin
    "dis2":   "#4ABFBB",  # Dolphin light
    "ssocks":  "#DD0001", # UiO
    "ssocks2": "#FF1112", # UiO light
    "sisci":  "#CF24AA",  # Pink
    "sisci2": "#DF47BE",  # Pink light
    "ib":     "#76B900",  # Nvidia
    "ib2":    "#97EC00",  # Nvidia light
}


# Argument parser
parser = argparse.ArgumentParser(description='Plot data using a configuration file.')

parser.add_argument('--out_file', type=str, required=True, help='The name of the output image file.')
parser.add_argument('--title', type=str, default='', help='The title of the plot.')
parser.add_argument('--rw', type=str, required=True, help='The type of I/O operation (read/write).')
parser.add_argument('--jobs', type=str, nargs='+', required=True, help='The names of the jobs to plot.')
parser.add_argument('--labels', type=str, nargs='+', default=[], help='The labels for each job.')
parser.add_argument('--x_label', type=str, default='Block Size (KB)', help='The label for the x-axis.')
parser.add_argument('--y_label', type=str, default='Throughput (MB/s)', help='The label for the y-axis.')
parser.add_argument('--colors', type=str, nargs='+', required=True, help='The colors for each job.')
parser.add_argument('--markers', type=str, nargs='+', default=[], help='The markers for each job.')
parser.add_argument('--height', type=int, default=6, help='The height of the plot.')
parser.add_argument('--width', type=int, default=8, help='The width of the plot.')
parser.add_argument('--x_scale', type=str, default='linear', help='The scale of the x-axis.')
parser.add_argument('--y_scale', type=str, default='linear', help='The scale of the y-axis.')
parser.add_argument('--style', type=str, default='seaborn-v0_8-paper', help='The style of the plot.')

parser.add_argument('--dpi', type=int, default=300, help='The DPI of the output image.')


args = parser.parse_args()

OUT_FILE = args.out_file
TITLE = args.title
RW = args.rw
jobs = args.jobs
LABELS = args.labels
X_LABEL = args.x_label
Y_LABEL = args.y_label
COLORS = args.colors
MARKERS = args.markers
HEIGHT = args.height
WIDTH = args.width
X_SCALE = args.x_scale
Y_SCALE = args.y_scale
STYLE = args.style
DPI = args.dpi


num_jobs = len(jobs)

# Ensure the number of labels matches the number of jobs.
if len(LABELS) != num_jobs and num_jobs > 1:
    print('Number of labels does not match the number of jobs.')
    sys.exit(1)



# If markers are not provided, use the default marker cycle.
if not args.markers:
    MARKERS = ['o' for _ in range(num_jobs)]
    plt.rcParams['axes.prop_cycle'] += cycler(marker=MARKERS)


# Create the plot.
plt.figure(figsize=(WIDTH, HEIGHT))

# Loop over each job.
for i, job in enumerate(jobs):

    # Construct the input path.
    input_path = os.path.join(DATA_DIR, job)
    
    # Load the JSON data.
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    # Initialize lists to store block sizes and throughputs.
    block_sizes = []
    throughputs = []
    
    # Process each job entry in the JSON.
    for sub_job in data.get('jobs', []):
        sub_job_str = sub_job.get('jobname', '')
        try:
            # Assume the block size is the second token in the job name (e.g., "job_4k").
            bs_str = sub_job_str.split('_')[1]
        except IndexError:
            print(f'Invalid job name "{sub_job_str}" in {input_path}')
            sys.exit(1)

        # Convert the block size string to a numeric value in KB.
        bs_str_lower = bs_str.lower()

        if bs_str_lower.endswith('k'):
            bs_kb = float(bs_str_lower.rstrip('k'))
        elif bs_str_lower.endswith('m'):
            bs_kb = float(bs_str_lower.rstrip('m')) * 1024
        else:
            bs_kb = float(bs_str) / 1024.0

        # Append the block size to the list.
        block_sizes.append(bs_kb)

        # Retrieve the write bandwidth in KB/s, then convert to MB/s.
        bw_kb = sub_job.get(RW, {}).get('bw', 0)
        bw_mb = bw_kb / 1024.0

        # Append the throughput to the list.
        throughputs.append(bw_mb)


    # If valid data was found, sort it by block size and plot.
    if block_sizes and throughputs:
        sorted_data = sorted(zip(block_sizes, throughputs))
        block_sizes, throughputs = zip(*sorted_data)
        plt.plot(block_sizes, throughputs, color=palette[COLORS[i]], marker=MARKERS[i], linestyle='-', label=LABELS[i])
    else:
        print(f'No valid data found in {input_path}')


# Customization
plt.style.use(STYLE)
ax = plt.gca()  # Get current axes
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xlabel(X_LABEL)
plt.ylabel(Y_LABEL)
plt.title(TITLE)
plt.grid(True)
plt.xscale(X_SCALE)
plt.yscale(Y_SCALE)


# Add a legend if more than one job was plotted.
if num_jobs > 1: (plt.legend())

# Save the plot to the designated output path.

plt.savefig(OUT_FILE, dpi=DPI)
print(f'OUT: {OUT_FILE}')



