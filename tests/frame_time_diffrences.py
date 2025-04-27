import os,textwrap
import statistics
from collections import Counter
import matplotlib.pyplot as plt
from vaapi.client import Vaapi

def plot_frame_times_combined(logs):
    # Create a figure with 3 subplots (1 row, 3 columns)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Frame Time Differences Across Logs', fontsize=16)
    
    # Process each log and plot in the corresponding subplot
    for i, log in enumerate(logs):
        # Get frames for this log
        motionframes = client.motionframe.list(log=log.id)
        cognitionframes = client.cognitionframe.list(log=log.id)
        
        # Sort frames by frame number
        def sort_frame_key_fn(frame):
            return frame.frame_number
        motionframes = sorted(motionframes, key=sort_frame_key_fn)
        
        # Calculate time differences
        time_diff = []
        for x in range(len(motionframes)-1):
            time_diff.append(motionframes[x+1].frame_time - motionframes[x].frame_time)
        
        # Print statistics for this log
        print(f"Log {log.id} statistics:")
        print(f"Max: {max(time_diff)}")
        print(f"Min: {min(time_diff)}")
        print(f"Mean: {statistics.mean(time_diff)}")
        print(f"Unique values: {set(time_diff)}")
        print("-" * 40)
        
        # Calculate frequencies
        frequencies = Counter(time_diff)
        values = list(frequencies.keys())
        counts = list(frequencies.values())
        
        # Plot on the corresponding subplot
        ax = axes[i]
        x_positions = range(len(values))
        bars = ax.bar(x_positions, counts)
        
        # Set labels and title
        ax.set_xlabel('Time Difference Values')
        ax.set_ylabel('Frequency')
        ax.set_title('\n'.join(textwrap.wrap(log.sensor_log_path, width=50)))
        ax.set_xticks(x_positions)
        ax.set_xticklabels(values, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)

        
        # Add count labels above bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    str(count), ha='center', va='bottom')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Make room for the suptitle
    plt.show()

if __name__ == "__main__":
    client = Vaapi(
        base_url=os.environ.get("VAT_API_URL"),
        api_key=os.environ.get("VAT_API_TOKEN"),
    )
    
    # Get the logs
    log1 = client.logs.get(id=1)
    log100 = client.logs.get(id=100)
    log200 = client.logs.get(id=200)
    
    # Plot all three logs in one figure with subplots
    plot_frame_times_combined([log1, log100, log200])