# Code for the Arduino Nano Every using Latop and sensor is plugged into COM5

import serial
import matplotlib.pyplot as plt
import numpy as np

# Open the serial port
ser = serial.Serial('COM5', 9600) # Change 'COM3' to the port where your Arduino is connected

# Create a blank figure
fig = plt.figure()
ax = fig.add_subplot(111)
plt.ion()

fig.show()
fig.canvas.draw()

# Start with an empty data array
data = []

# Read and plot the data
# while True:
#   if ser.inWaiting():
#     # Read a line from the serial port
#     line = ser.readline()
    
#     # Convert the bytes to a string, then to an integer
#     value = int(line.decode("utf-8").strip())
    
#     # Append the data to the array
#     data.append(value)
    
#     # Plot the data
#     ax.clear()
#     ax.plot(data)
#     fig.canvas.draw()