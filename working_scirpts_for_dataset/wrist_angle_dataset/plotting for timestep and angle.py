import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_data(dataset, filepath):
    # Extract the filename from the path and use it as the title
    filename = os.path.basename(filepath).split('.')[0]
    title = f'Data from {filename}'
    
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Outer forearm sensor value
    axs[0].plot(dataset['timestamp'], dataset['Outer forearm sensor value (1)'], color='blue', label='Outer forearm sensor value')
    axs[0].set_ylabel('Outer forearm sensor value')
    axs[0].legend(loc='upper right')
    
    # Inner forearm sensor value
    axs[1].plot(dataset['timestamp'], dataset['Inner forearm sensor value (2)'], color='red', label='Inner forearm sensor value')
    axs[1].set_ylabel('Inner forearm sensor value')
    axs[1].legend(loc='upper right')
    
    # Angle
    axs[2].plot(dataset['timestamp'], dataset['angle'], color='green', label='Angle')
    axs[2].set_xlabel('Timestamp')
    axs[2].set_ylabel('Angle')
    axs[2].legend(loc='upper right')
    
    fig.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    
    # Check if the Plots folder exists. If not, create it
    plot_dir = os.path.join(os.path.dirname(filepath), 'Plots')
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    
    # Save the plot to the Plots folder
    plot_path = os.path.join(plot_dir, f'{filename}.png')
    plt.savefig(plot_path)
    plt.close()

def main():
    # Define the paths to your CSV files here
    csv_paths = [
        "working_scirpts_for_dataset/wrist_angle_dataset/previous_recordings/wrist+angle_recording_1691760899/merged_dataset_closest_timestep.csv",
        "working_scirpts_for_dataset/wrist_angle_dataset/previous_recordings/wrist+angle_recording_1691760899/merged_dataset_linear_regression.csv",
        "working_scirpts_for_dataset/wrist_angle_dataset/previous_recordings/wrist+angle_recording_1691760899/merged_dataset_version_2_linear_regression+interpolation.csv",
        "working_scirpts_for_dataset/wrist_angle_dataset/previous_recordings/wrist+angle_recording_1691760899/merged_interpolated_dataset_closest_timestep.csv"
    ]

    for path in csv_paths:
        data = pd.read_csv(path)
        plot_data(data, path)

if __name__ == "__main__":
    main()
