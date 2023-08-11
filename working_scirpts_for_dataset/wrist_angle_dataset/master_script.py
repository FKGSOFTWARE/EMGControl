
import os
import time
import shutil

# Paths
input_dir = "working_scirpts_for_dataset/wrist_angle_dataset/__input"
output_dir = "working_scirpts_for_dataset/wrist_angle_dataset/_output"
mediapipe_script = "working_scirpts_for_dataset/wrist_angle_dataset/mediapipe_hand+body+angle copy.py"
previous_recordings_dir = "working_scirpts_for_dataset/wrist_angle_dataset/previous_recordings"

# Wait for .mp4 and .csv files to appear in the input directory
while True:
    files = os.listdir(input_dir)
    if any(f.endswith('.mp4') for f in files) and any(f.endswith('.csv') for f in files):
        break
    time.sleep(10)  # Wait for 10 seconds before checking again

# Get the .mp4 file name
mp4_file = [f for f in files if f.endswith('.mp4')][0]

# Prompt user for time and date
date_input = input("Please enter the date (e.g., YYYY-MM-DD): ")
time_input = input("Please enter the time including milliseconds (e.g., HH:MM:SS:MSMSMS): ")

# Run the mediapipe script
os.system(f"python {{mediapipe_script}} --video {{os.path.join(input_dir, mp4_file)}} --date {{date_input}} --time {{time_input}}")

# Create a new directory with the current unix timestamp
current_unix_time = str(int(time.time()))
new_folder_name = f"wrist+angle_recording_{{current_unix_time}}"
new_folder_path = os.path.join(previous_recordings_dir, new_folder_name)
os.makedirs(new_folder_path)

# Move files from input and output directories to the new folder
for file in os.listdir(input_dir):
    shutil.move(os.path.join(input_dir, file), new_folder_path)

for file in os.listdir(output_dir):
    shutil.move(os.path.join(output_dir, file), new_folder_path)

print(f"Processing complete! Files have been moved to {{new_folder_path}}")
