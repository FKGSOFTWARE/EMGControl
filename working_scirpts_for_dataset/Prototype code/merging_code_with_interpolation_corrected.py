
import pandas as pd

# Load the datasets
arm_angle_df = pd.read_csv("working_scirpts_for_dataset/wrist_angle_dataset/_output/TA_body_and_hand_landmarks_data_TimeVideo_20230808_160537.csv")
emg_df = pd.read_csv("working_scirpts_for_dataset/wrist_angle_dataset/__input/test in frame.csv")
# Convert "x" to NaN and then interpolate
arm_angle_df['angle'] = pd.to_numeric(arm_angle_df['angle'], errors='coerce')
arm_angle_df['angle'].interpolate(method='linear', inplace=True)

# Merge datasets based on the closest timestamps
def find_nearest_angle(timestamp):
    diffs = abs(arm_angle_df['global_timestamp_ms'] - timestamp)
    idx_min_diff = diffs.idxmin()
    return arm_angle_df.iloc[idx_min_diff]['angle']

emg_df['angle'] = emg_df['global_time'].apply(find_nearest_angle)


# Save the merged dataset
emg_df.to_csv("working_scirpts_for_dataset/wrist_angle_dataset/_output/c_merged_interpolated_dataset.csv", index=False)
