import datetime
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import time

time_from_video_timestamp = "16:05:37.246"
date_of_video_timestamp = "2023-08-08"

folder_in_use = "working_scirpts_for_dataset/wrist_angle_dataset/__input/"
filename = "TimeVideo_20230808_160537.mp4"
file_in_use = folder_in_use + filename

datetime_from_video_timestamp = (
    date_of_video_timestamp + " " + time_from_video_timestamp
)
dt = datetime.datetime.strptime(datetime_from_video_timestamp, "%Y-%m-%d %H:%M:%S.%f")
timestamp = dt.timestamp()
difference_in_time = time.time() - timestamp
start_timestamp_ms = time.time() - difference_in_time

# Initialize MediaPipe Hands and Pose
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)
pose = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Open video file
cap = cv2.VideoCapture(file_in_use)

fps = cap.get(cv2.CAP_PROP_FPS)

# Initialize VideoWriter
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(
    "working_scirpts_for_dataset/wrist_angle_dataset/_output/body_and_hand_output_" + filename,
    fourcc,
    fps,
    (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),
)

# Prepare data storage for landmarks and timestamps
landmarks_data = []
frame_idx = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands and Pose
    hand_results = hands.process(rgb_frame)
    pose_results = pose.process(rgb_frame)

    # Draw hand landmarks on the frame
    if hand_results.multi_hand_landmarks:
        for hand_landmarks in hand_results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            for id, lm in enumerate(hand_landmarks.landmark):
                landmarks_data.append(
                    [
                        "hand",
                        start_timestamp_ms + (frame_idx / fps),
                        frame_idx / fps * 1000,
                        id,
                        lm.x,
                        lm.y,
                        lm.z,
                    ]
                )

    # Draw pose landmarks on the frame
    if pose_results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

        for id, lm in enumerate(pose_results.pose_landmarks.landmark):
            # global_timestamp_ms = (time.time() - difference_in_time)

            landmarks_data.append(
                [
                    "pose",
                    start_timestamp_ms + (frame_idx / fps),
                    frame_idx / fps * 1000,
                    id,
                    lm.x,
                    lm.y,
                    lm.z,
                ]
            )

    # Write the frame to the output video file
    out.write(frame)

    frame_idx += 1

cap.release()
out.release()

# Convert landmarks_data to a pandas DataFrame and save to a .csv file
landmarks_df = pd.DataFrame(
    landmarks_data,
    columns=[
        "landmark_type",
        "global_timestamp_ms",
        "video_timestamp_ms",
        "landmark_id",
        "x",
        "y",
        "z",
    ],
)
landmarks_df.to_csv(
    "working_scirpts_for_dataset/wrist_angle_dataset/_output/body_and_hand_landmarks_data_" + filename[:-4] + ".csv", index=False
)
