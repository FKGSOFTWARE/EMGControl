
import pandas as pd
import os
from datetime import datetime

# Example file path (replace this with your actual file path)
arm_angle_file_path = "working_scirpts_for_dataset/wrist_angle_dataset/previous_recordings/wrist+angle_recording_1691760899/TA_body_and_hand_landmarks_data_TimeVideo_20230808_160537.csv"
emg_file_path = "working_scirpts_for_dataset/wrist_angle_dataset/previous_recordings/wrist+angle_recording_1691760899/test in frame.csv"

arm_angle_filename = os.path.basename(arm_angle_file_path)
emg_filename = os.path.basename(emg_file_path)

current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Load the datasets
arm_angle_df = pd.read_csv(arm_angle_file_path)
emg_df = pd.read_csv(emg_file_path)
# Convert "x" to NaN and then interpolate
arm_angle_df['angle'] = pd.to_numeric(arm_angle_df['angle'], errors='coerce')

# Using cubic spline interpolation for the 'angle' column. 
# The 'order' parameter specifies the order of the spline. 
# Cubic splines (order=3) are commonly used and provide a good balance between smoothness and fit.
# Adjust the 'order' parameter as needed. Higher orders may result in smoother curves but can also introduce oscillations.
arm_angle_df['angle'].interpolate(method='spline', order=3, inplace=True)

# Merge datasets based on the closest timestamps
def find_nearest_angle(timestamp):
    diffs = abs(arm_angle_df['global_timestamp_ms'] - timestamp)
    idx_min_diff = diffs.idxmin()
    return arm_angle_df.iloc[idx_min_diff]['angle']

emg_df['angle'] = emg_df['global_time'].apply(find_nearest_angle)

# Save the merged dataset
emg_df.to_csv("working_scirpts_for_dataset/wrist_angle_dataset/_output/spline_interpolation_"+arm_angle_filename[:-4]+"_"+current_datetime+".csv", index=False)