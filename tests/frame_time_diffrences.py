import os,textwrap
import statistics
from collections import Counter
import matplotlib.pyplot as plt
from vaapi.client import Vaapi

def plot_frame_data(ax,time_diff,title,sensor_log_path):
    frequencies = Counter(time_diff)
    values = list(frequencies.keys())
    counts = list(frequencies.values())
    
    # Plot the data
    x_positions = range(len(values))
    ax.bar(x_positions, counts)
    
    # Set labels and title
    ax.set_xlabel('Time Difference Values')
    ax.set_ylabel('Frequency')
    formatted_path = "\n".join(textwrap.wrap(sensor_log_path, width=50))
    ax.set_title(f"{title}\n{formatted_path}")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(values, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    
    
def plot_frame_times_combined(logs):
   
    figures = []
    
    # Page 1: Motion Frames for all logs
    fig_motion = plt.figure(figsize=(18, 8))
    fig_motion.suptitle('Motion Frame Time Differences Across Logs', fontsize=16)
    figures.append(fig_motion)
    
    # Create a 1x3 grid for motion frames
    axes_motion = []
    for i in range(3):
        ax = fig_motion.add_subplot(1, 3, i+1)
        axes_motion.append(ax)
    
    # Page 2: Cognition Frames for all logs
    fig_cognition = plt.figure(figsize=(18, 8))
    fig_cognition.suptitle('Cognition Frame Time Differences Across Logs', fontsize=16)
    figures.append(fig_cognition)
    
    # Create a 1x3 grid for cognition frames
    axes_cognition = []
    for i in range(3):
        ax = fig_cognition.add_subplot(1, 3, i+1)
        axes_cognition.append(ax)
    
    # Process each log and plot in the corresponding subplot
    for i, log in enumerate(logs):
        # Get frames for this log
        motionframes = client.motionframe.list(log=log.id)
        cognitionframes = client.cognitionframe.list(log=log.id)
        
        # Sort frames by frame number
        def sort_frame_key_fn(frame):
            return frame.frame_number
        motionframes = sorted(motionframes, key=sort_frame_key_fn)
        cognitionframes = sorted(cognitionframes, key=sort_frame_key_fn)
        
        # Calculate time differences for motion frames
        motion_time_diff = []
        for x in range(len(motionframes)-1):
            motion_time_diff.append(motionframes[x+1].frame_time - motionframes[x].frame_time)
        
        cognition_time_diff = []
        for x in range(len(cognitionframes)-1):
            cognition_time_diff.append(cognitionframes[x+1].frame_time - cognitionframes[x].frame_time)

    
        plot_frame_data(axes_motion[i], motion_time_diff, f'Log ID: {log.id} - Motion Frames', log.sensor_log_path)
        
        plot_frame_data(axes_cognition[i], cognition_time_diff, f'Log ID: {log.id} - Cognition Frames', log.sensor_log_path)
    
   # Adjust layout for both figures
    for fig in figures:
        fig.tight_layout(rect=[0, 0.05, 1, 0.95])
        fig.subplots_adjust(bottom=0.25)
    
    # Show plots - this will display them with navigation buttons in the UI
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