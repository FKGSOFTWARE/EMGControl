
import pandas as pd
import numpy as np

# Specify your file path here
file_path = "working_scirpts_for_dataset/wrist_angle_dataset/_output/body_and_hand_landmarks_data_TimeVideo_20230808_160537.csv"

def calculate_angle(hand_landmarks, pose_landmarks):
    # Extracting the required points
    point_A = hand_landmarks.loc[hand_landmarks['landmark_id'] == 0, ['x', 'y', 'z']].values[0]
    point_B = hand_landmarks.loc[hand_landmarks['landmark_id'] == 5, ['x', 'y', 'z']].values[0]
    point_C = hand_landmarks.loc[hand_landmarks['landmark_id'] == 17, ['x', 'y', 'z']].values[0]
    point_interest = pose_landmarks.loc[pose_landmarks['landmark_id'] == 14, ['x', 'y', 'z']].values[0]
    
    # Forming the vectors
    vector_AB = point_B - point_A
    vector_AC = point_C - point_A
    vector_AP_interest = point_interest - point_A

    # Normal vector of the plane formed by points A, B, C
    normal_vector = np.cross(vector_AB, vector_AC)

    # Projecting onto XY-plane
    normal_vector_projected = [normal_vector[0], normal_vector[1], 0]
    vector_AP_interest_projected = [vector_AP_interest[0], vector_AP_interest[1], 0]

    # Calculating the angle between the projections
    dot_product = np.dot(normal_vector_projected, vector_AP_interest_projected)
    magnitude_product = np.linalg.norm(normal_vector_projected) * np.linalg.norm(vector_AP_interest_projected)
    cos_theta = dot_product / magnitude_product
    angle = np.arccos(cos_theta) * 180 / np.pi

    return angle

def process_file(file_path):
    data_df = pd.read_csv(file_path)

    # Grouping by timestamp and calculating the angle
    unique_timestamps = data_df['global_timestamp_ms'].unique()
    angle_data = []
    ta_data = []

    for timestamp in unique_timestamps:
        timestamp_data = data_df[data_df['global_timestamp_ms'] == timestamp]
        hand_landmarks = timestamp_data[timestamp_data['landmark_type'] == 'hand']
        pose_landmarks = timestamp_data[timestamp_data['landmark_type'] == 'pose']

        # Check if required landmarks are available
        if all(landmark_id in hand_landmarks['landmark_id'].values for landmark_id in [0, 5, 17]) and            14 in pose_landmarks['landmark_id'].values:
            angle = calculate_angle(hand_landmarks, pose_landmarks)
        else:
            angle = None

        angle_data.extend([angle] * len(timestamp_data))
        ta_data.append({"global_timestamp_ms": timestamp, "angle": angle if angle else ""})

    # Adding the angle data as a new column
    data_df['angle'] = angle_data
    ta_df = pd.DataFrame(ta_data)

    # Saving the updated DataFrame to CSV files
    updated_file_path = "working_scirpts_for_dataset/wrist_angle_dataset/_output/updated_" + file_path.split("/")[-1]
    ta_file_path = "working_scirpts_for_dataset/wrist_angle_dataset/_output/TA_" + file_path.split("/")[-1]
    
    data_df.to_csv(updated_file_path, index=False)
    ta_df.to_csv(ta_file_path, index=False)
    
    print(f"Updated data saved to: {updated_file_path}")
    print(f"TA data saved to: {ta_file_path}")

# Run the processing function
process_file(file_path)

