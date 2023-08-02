import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Open video file
cap = cv2.VideoCapture("C:/Users/fkgde/Documents/PlatformIO/Projects/Internship 2023/output/official recordings/video/video mediapipe/test_video.mp4")

# cap = cv2.VideoCapture('path_to_your_video_file')
fps = cap.get(cv2.CAP_PROP_FPS)

# Initialize VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

# Prepare data storage for landmarks and timestamps
landmarks_data = []
frame_idx = 0

# Record the start time
start_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert the BGR image to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    results = hands.process(rgb_frame)

    # Draw hand landmarks on the frame
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Extract x, y, z coordinates and timestamps
            for id, lm in enumerate(hand_landmarks.landmark):
                # Get the global timestamp (current time - start time) in milliseconds
                global_timestamp_ms = (time.time() - start_time) * 1000
                landmarks_data.append([global_timestamp_ms, frame_idx / fps * 1000, id, lm.x, lm.y, lm.z])

    # Write the frame to the output video file
    out.write(frame)

    frame_idx += 1

cap.release()
out.release()

# Convert landmarks_data to a pandas DataFrame and save to a .csv file
landmarks_df = pd.DataFrame(landmarks_data, columns=['global_timestamp_ms', 'video_timestamp_ms', 'landmark_id', 'x', 'y', 'z'])
landmarks_df.to_csv('landmarks_data.csv', index=False)
