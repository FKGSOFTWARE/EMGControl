import numpy as np
import matplotlib.pyplot as plt
import serial
import time
from threading import Thread
from queue import Queue

class SerialReader:
    def __init__(self, port, baud_rate):
        self.ser = serial.Serial(port, baud_rate)
        self.ser.flushInput()  # Flush the serial input buffer
        self.data_queue = Queue()
        self.stop_thread = False
        self.thread = Thread(target=self.read_from_serial)
        self.thread.start()

    def read_from_serial(self):
        while not self.stop_thread:
            try:
                if self.ser.inWaiting():
                    line = self.ser.readline().decode("utf-8").strip()
                    timestamp, value = map(float, line.split(","))
                    self.data_queue.put((timestamp, value))
            except (OSError, serial.SerialException):
                print("Error reading from serial port")
                break
            except ValueError:
                print(f"Received invalid data: {line}")  # Print the received data

    def stop(self):
        self.stop_thread = True
        self.thread.join()
        self.ser.close()

class DataPlotter:
    def __init__(self, reader, plot_window=500):
        self.reader = reader
        self.plot_window = plot_window
        self.fig, self.ax = plt.subplots()

    def plot(self):
        time_data = []
        sensor_data = []
        while True:
            try:
                if not self.reader.data_queue.empty():
                    timestamp, value = self.reader.data_queue.get()
                    time_data.append(timestamp)
                    sensor_data.append(value)

                    # Only keep last plot_window data points
                    time_data = time_data[-self.plot_window:]
                    sensor_data = sensor_data[-self.plot_window:]

                    self.ax.clear()
                    self.ax.plot(time_data, sensor_data)
                    plt.pause(0.001)
                    print(self.reader.data_queue.qsize())
                    # self.reader.data_queue.clear()
                    self.reader.data_queue.queue.clear()
            except KeyboardInterrupt:
                break
        self.reader.stop()

if __name__ == "__main__":
    reader = SerialReader('COM5', 115200)
    plotter = DataPlotter(reader)
    plotter.plot()
