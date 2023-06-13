import serial
import matplotlib.pyplot as plt
import numpy as np  # Import numpy for the log function
from threading import Thread
from queue import Queue

# Open the serial port
ser = serial.Serial('COM5', 9600)  # Change to the port where your Arduino is connected

# Create two queues to hold the data
data_queue1 = Queue()
data_queue2 = Queue()

# This function will be run in a separate thread, reading data from the serial port
def read_from_serial(queue1, queue2):
    while True:
        if ser.inWaiting():
            line = ser.readline()
            # Split the line into two values
            values = line.decode("utf-8").strip().split(',')
            queue1.put(int(values[0]))  # Add the first value to the first queue
            queue2.put(int(values[1]))  # Add the second value to the second queue

# Start the read_from_serial function in a new thread
thread = Thread(target=read_from_serial, args=(data_queue1, data_queue2,))
thread.start()

# Create a blank figure for plotting
plt.ion()
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)  # Create four subplots

# Start with empty data arrays
data1 = []
data2 = []

# Read data from the queue and plot it
while True:
    # If there's data in the queues, read it and plot it
    if not data_queue1.empty():
        value1 = data_queue1.get()
        data1.append(value1)
        ax1.clear()
        ax1.plot(data1)
        ax1.set_title("Sensor 1 from A0")
        
        ax3.clear()
        ax3.plot(np.log(data1))  # Plot the log of the data
        ax3.set_title("Log Sensor 1 (A0)")
        
    if not data_queue2.empty():
        value2 = data_queue2.get()
        data2.append(value2)
        ax2.clear()
        ax2.plot(data2)
        ax2.set_title("Sensor 2 from A1")
        
        ax4.clear()
        ax4.plot(np.log(data2))  # Plot the log of the data
        ax4.set_title("Log Sensor 2 (A1)")
        
    plt.pause(0.01)  # Pause to allow the plot to update