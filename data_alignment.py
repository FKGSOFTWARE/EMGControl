import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df1 = pd.read_csv('output/official recordings/video/video mediapipe/test_video_landmarks_data.csv')
df2 = pd.read_csv('output/official recordings/video/video mediapipe/test_video_sensor_data.csv')

print("df1.columns = ", df1.columns)
print("df2.columns = ", df2.columns)

# Plot the timestamp columns
plt.figure(figsize=(10,6))

# Plot timestamps from the first dataframe
plt.plot(df1['global_timestamp_ms'], label='global_timestamp_ms')
plt.plot(df1['video_timestamp_ms'], label='video_timestamp_ms')
plt.plot(df1['landmark_id'], label='landmark_id')
plt.plot(df1['x'], label='x')
plt.plot(df1['y'], label='y')
plt.plot(df1['z'], label='z')

# Plot timestamps from the second dataframe
plt.plot(df2['timestamp'], label='timestamp')
plt.plot(df2['Outer forearm sensor value (1)'], label='Outer forearm sensor value (1)')
plt.plot(df2['Inner forearm sensor value (2)'], label='Inner forearm sensor value (2)')

plt.title('Timestamps from Two Sensors')
plt.xlabel('Index')
plt.ylabel('Timestamp (ms)')
plt.legend()

plt.show()
