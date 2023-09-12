# import subprocess
# import json

# def extract_video_metadata(video_path):
#     cmd = [
#         'ffprobe',
#         '-v', 'quiet',
#         '-print_format', 'json',
#         '-show_format',
#         '-show_streams',
#         video_path
#     ]

#     result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#     return json.loads(result.stdout)

# # video_path = 'path_to_your_video.mp4'
# metadata = extract_video_metadata(video_path)

# # If you want to extract the creation time:
# creation_time = metadata['format'].get('tags', {}).get('creation_time', None)
# print(creation_time)


# import imageio_ffmpeg as ffmpeg

# def extract_video_metadata(video_path):
#     info = ffmpeg.probe(video_path)
#     return info

# # video_path = 'path_to_your_video.mp4'
# video_path = "output/official recordings/video/video mediapipe/test_video.mp4"

# metadata = extract_video_metadata(video_path)

# # If you want to extract the creation time:
# creation_time = metadata['format'].get('tags', {}).get('creation_time', None)
# print(creation_time)

import subprocess
import json
import time

def extract_video_metadata(video_path):
    cmd = [
        'ffprobe',  # Or provide the full path to ffprobe if it's not in the PATH
        # "C:/python38/lib/site-packages/ffprobe/ffprobe.py",
        '-hide_banner',
        '-loglevel', 'panic',  # suppresses most of the command-line output
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return json.loads(result.stdout)

# video_path = 'path_to_your_video.mp4'
video_path = "output/official recordings/video/video mediapipe/TimeVideo_20230808_144011.mp4"

metadata = extract_video_metadata(video_path)

# If you want to extract the creation time:
creation_time = metadata['format'].get('tags', {}).get('creation_time', None)
print(creation_time)

print(metadata)

import datetime
import time

# Get the current time in seconds since the epoch
current_time_seconds = time.time()

# Convert it to a datetime object
current_datetime = datetime.datetime.fromtimestamp(current_time_seconds)

# Format the datetime object
formatted_time = current_datetime.strftime('%H:%M:%S.%f')[:-3]  # We're slicing to get only 3 decimal places for milliseconds

print(formatted_time)
