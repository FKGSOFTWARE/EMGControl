
import pandas as pd

# Load the datasets
arm_angle_df = pd.read_csv("working_scirpts_for_dataset/wrist_angle_dataset/_output/TA_body_and_hand_landmarks_data_TimeVideo_20230808_160537.csv")
emg_df = pd.read_csv("working_scirpts_for_dataset/wrist_angle_dataset/__input/test in frame.csv")

# Defining a function to find the closest timestamp in the arm_angle_df
def find_nearest_angle(timestamp):
    # Compute absolute differences between the given timestamp and all timestamps in arm_angle_df
    diffs = abs(arm_angle_df['global_timestamp_ms'] - timestamp)
    # Get the index of the minimum difference
    idx_min_diff = diffs.idxmin()
    # Return the angle corresponding to the timestamp with the smallest difference
    return arm_angle_df.iloc[idx_min_diff]['angle']

# Apply the function to the global_time column of the emg_df
emg_df['angle'] = emg_df['global_time'].apply(find_nearest_angle)

# Save the merged dataset
emg_df.to_csv("working_scirpts_for_dataset/wrist_angle_dataset/_output/merged_dataset.csv", index=False)
