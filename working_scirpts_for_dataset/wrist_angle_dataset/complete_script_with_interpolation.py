
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

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

# Interpolate NaN values in the 'angle' column after merging
emg_df['angle'].interpolate(method='linear', inplace=True)

# Diagnostic step to check for NaN values (optional, can be removed later)
num_nan_values_in_angle = emg_df['angle'].isna().sum()
print(f"Number of NaN values in the 'angle' column after interpolation: {num_nan_values_in_angle}")

# Linear Regression
X = emg_df[['Outer forearm sensor value (1)', 'Inner forearm sensor value (2)']]
y = emg_df['angle']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a linear regression model
model = LinearRegression().fit(X_train, y_train)

# Predict on test set
y_pred = model.predict(X_test)

# Compute RMSE
rmse = mean_squared_error(y_test, y_pred, squared=False)
print(f"Root Mean Squared Error (RMSE): {rmse}")

# Save the merged dataset
emg_df.to_csv("merged_dataset_version_2_corrected.csv", index=False)
