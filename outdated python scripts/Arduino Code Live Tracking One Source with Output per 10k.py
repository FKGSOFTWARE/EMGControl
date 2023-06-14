import serial
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread
from queue import Queue
import pandas as pd
import os

# Open the serial port
ser = serial.Serial('COM5', 9600) # Change to the port where your Arduino is connected

# Create a queue to hold the data
data_queue = Queue()

# This function will be run in a separate thread, reading data from the serial port
def read_from_serial(queue):
    while True:
        if ser.inWaiting():
            line = ser.readline()
            value = int(line.decode("utf-8").strip())
            queue.put(value)  # Add the value to the queue

# Start the read_from_serial function in a new thread
thread = Thread(target=read_from_serial, args=(data_queue,))
thread.start()

# Create a blank figure for plotting
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111)

# Start with an empty data array
data = []

# Counter for the output file
file_counter = 1

# Read data from the queue and plot it
while True:
    # If there's data in the queue, read it and plot it
    if not data_queue.empty():
        value = data_queue.get()
        data.append(value)
        ax.clear()
        ax.plot(data)
        plt.pause(0.01)  # Pause to allow the plot to update

        # If the size of data has reached 10000, save it to a .csv file
        if len(data) >= 100:
            df = pd.DataFrame(data)
            filename = os.path.join('output', f'data_{file_counter}.csv')
            df.to_csv(filename, index=False, header=False)
            print(f"Data saved to {filename}")
            data = []  # Clear the data list
            file_counter += 1  # Increment the file counter
