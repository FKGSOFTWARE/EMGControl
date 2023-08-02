import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import numpy as np
import time
import os
import glob
import pandas as pd

# STEP 1: Define time
# Function to get current time in milliseconds
def current_milli_time():
    return round(time.time() * 1000)


# # STEP 2: Video to np.array 
# # Specify the directory which contains the video
# video_dir = 'C:/Users/fkgde/Documents/PlatformIO/Projects/Internship 2023/output/official recordings/video/video mediapipe'

# # Find any video file format (e.g., mp4, avi, etc.)
# video_files = glob.glob(os.path.join(video_dir, '*.*'))

# # Assuming there's only one video file in the directory
# video_file = video_files[0]


# Create a VideoCapture object
cap = cv2.VideoCapture("C:/Users/fkgde/Documents/PlatformIO/Projects/Internship 2023/output/official recordings/video/video mediapipe/20230802_112816.mp4")

# Check if camera opened successfully
if not cap.isOpened(): 
    print("Error opening video file")

# Read until video is completed
frames = []
while(cap.isOpened()):
  
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:

    # Append the frame to the frames list
    frames.append(frame)

  # Break the loop
  else: 
    break

# Convert list of frames into a NumPy array
video_as_np_array = np.array(frames)
# print(len(video_as_np_array))
cap.release()




# STEP 3: Initialize the MediaPipe HandLandmarker
model_path = 'C:/Users/fkgde/Documents/PlatformIO/Projects/Internship 2023/hand_landmarker.task'

mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=video_as_np_array)

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a hand landmarker instance with the video mode:
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path = model_path ),
    running_mode=VisionRunningMode.VIDEO)


frame_count = 0
# STEP 4: Process the video frames with the hand landmarker
with HandLandmarker.create_from_options(options) as landmarker:
    # The landmarker is initialized. Use it here.
    
    # frame_timestamp_ms = current_milli_time()
    # frame_timestamp_ms = int(round(frame_count * (1000/30)))
    frame_timestamp_ms = int(round(cap.get(cv2.CAP_PROP_POS_MSEC)))
    print(frame_timestamp_ms)
    hand_landmarker_result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
    frame_count += 1
    print(hand_landmarker_result)

# When everything is done, release the video capture object


# # STEP 5: Process the results to np.array
# # Assuming each hand_landmarks has 21 landmarks (according to MediaPipe documentation)
# num_landmarks = 21

# # Initialize a list to store the data for all hands
# hand_landmarks_data = []

# for hand_landmarks in hand_landmarker_result:
#     # Initialize a list to store the data for one hand
#     one_hand_data = []
#     for landmark in hand_landmarks.landmark:
#         # Append the x, y, and z coordinates to the list
#         one_hand_data.append([landmark.x, landmark.y, landmark.z])
#     # Append the data for one hand to the data for all hands
#     hand_landmarks_data.append(one_hand_data)

# # Convert the list of lists to a NumPy array
# hand_landmarks_np = np.array(hand_landmarks_data)

# # Now, hand_landmarks_np is a three-dimensional NumPy array where the first dimension
# # indexes the hand, the second dimension indexes the landmark, and the third dimension
# # indexes the coordinate (0 for x, 1 for y, 2 for z).



# # STEP 6: Save the results to CSV
# # Flatten the hand and landmark dimensions into one dimension
# flattened_data = hand_landmarks_np.reshape(hand_landmarks_np.shape[0], -1)

# # Create a list of column headers
# column_headers = []
# for hand_index in range(hand_landmarks_np.shape[0]):
#     for landmark_index in range(hand_landmarks_np.shape[1]):
#         for coordinate in ['x', 'y', 'z']:
#             column_headers.append(f'hand{hand_index}_landmark{landmark_index}_{coordinate}')
# column_headers.append('timestamp')

# # Convert the flattened data and the timestamp to a DataFrame
# df = pd.DataFrame(np.hstack([flattened_data, frame_timestamp_ms]), columns=column_headers)

# # Save the DataFrame to a CSV file
# df.to_csv('hand_landmarks.csv', index=False)













#   # STEP 5: Process the classification result. In this case, visualize it.
# annotated_image = draw_landmarks_on_image(image.numpy_view(), hand_landmarker_result)
# cv2_imshow(cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

# import cv2
# import numpy as np
# from mediapipe.python.solutions import drawing_utils as mp_drawing

# # Specify the path to the video file
# video_file = '/path/to/your/video'

# # Create a VideoCapture object
# cap = cv2.VideoCapture(video_file)

# # Check if video opened successfully
# if not cap.isOpened(): 
#     print("Error opening video file")

# # Read until video is completed
# while(cap.isOpened()):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#     if ret == True:
#         # Process the frame with MediaPipe HandLandmarker
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         hand_landmarks = landmarker.process(frame)
        
#         # Draw the hand landmarks on the frame
#         annotated_image = mp_drawing.draw_landmarks(frame, hand_landmarks)

#         # Convert the image from RGB to BGR (for display purposes)
#         annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR)

#         # Display the frame
#         cv2.imshow('Frame', annotated_image)

#         # Press Q on keyboard to exit
#         if cv2.waitKey(25) & 0xFF == ord('q'):
#             break
#     else: 
#         break

# # When everything is done, release the video capture object and close all frames
# cap.release()
# cv2.destroyAllWindows()
