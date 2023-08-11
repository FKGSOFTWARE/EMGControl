
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime

# Load the "TA_" prefixed CSV file
file_path = "TA_1body_and_hand_landmarks_data_TimeVideo_20230808_160537.csv"
ta_df = pd.read_csv(file_path)

# Convert 'x' to NaN and then interpolate
ta_df['angle'] = pd.to_numeric(ta_df['angle'], errors='coerce')
ta_df['angle'].fillna(method='backfill', inplace=True)
ta_df['angle'].interpolate(method='linear', inplace=True)

# Setting up the figure, axis, and plot elements
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_aspect('equal', 'box')
ax.grid(True)

# Creating a stationary bar (horizontal line)
ax.plot([0, 0], [-1, 1], 'b-')

# Creating a line (mobile bar) for the animation
line, = ax.plot([], [], 'r-', lw=2)
time_text = ax.text(0.85, 0.9, '', transform=ax.transAxes)

def init():
    """Initialize the line in its starting position."""
    line.set_data([], [])
    time_text.set_text('')
    return line, time_text

def animate(i):
    """Update the line for frame i."""
    x = [0, -np.cos(np.radians(ta_df.iloc[i]['angle']))]
    y = [0, np.sin(np.radians(ta_df.iloc[i]['angle']))]
    line.set_data(x, y)

    # Correctly converting the epoch timestamp to human-readable date and time
    timestamp = ta_df.iloc[i]['global_timestamp_ms']   # converting to seconds
    formatted_time = datetime.datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S.%f')[:-3]
    time_text.set_text(formatted_time)
    
    return line, time_text

ani = FuncAnimation(fig, animate, frames=len(ta_df), init_func=init, blit=True, interval=100)

# Pause functionality
is_paused = False
def toggle_pause(event):
    global is_paused
    if event.key == ' ':
        if is_paused:
            ani.event_source.start()
            is_paused = False
        else:
            ani.event_source.stop()
            is_paused = True

fig.canvas.mpl_connect('key_press_event', toggle_pause)

# Display the animation
plt.title("Angle Animation Over Time")
plt.show()

