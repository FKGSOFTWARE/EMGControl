
import os
import time
import shutil

# Paths
input_dir = "working_scirpts_for_dataset/wrist_angle_dataset/__input"
output_dir = "working_scirpts_for_dataset/wrist_angle_dataset/_output"
previous_recordings_dir = "working_scirpts_for_dataset/wrist_angle_dataset/previous_recordings"

# Create a new directory with the current unix timestamp
current_unix_time = str(int(time.time()))
new_folder_name = f"wrist+angle_recording_{current_unix_time}"
new_folder_path = os.path.join(previous_recordings_dir, new_folder_name)
os.makedirs(new_folder_path)

# Move files from input and output directories to the new folder
for file in os.listdir(input_dir):
    shutil.move(os.path.join(input_dir, file), new_folder_path)

for file in os.listdir(output_dir):
    shutil.move(os.path.join(output_dir, file), new_folder_path)

print(f"Files have been moved to {new_folder_path}")
