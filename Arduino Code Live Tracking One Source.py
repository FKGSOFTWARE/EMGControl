import serial
import matplotlib.pyplot as plt
import numpy as np
from threading import Thread
from queue import Queue

# Open the serial port
ser = serial.Serial('COM5', 9600) # Change 'COM3' to the port where your Arduino is connected

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

# Read data from the queue and plot it
while True:
    # If there's data in the queue, read it and plot it
    if not data_queue.empty():
        value = data_queue.get()
        data.append(value)
        ax.clear()
        ax.plot(data)
        plt.pause(0.01)  # Pause to allow the plot to update
