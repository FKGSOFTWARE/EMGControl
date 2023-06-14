import serial
from threading import Thread
from queue import Queue
import pyqtgraph as pg
from pyqtgraph.Qt.QtWidgets import QApplication
from pyqtgraph.Qt import QtCore

class SerialReader:
    """
    This class manages the serial connection to your Arduino device.
    It runs a secondary thread that reads the serial data and adds it to a queue, for processing by the main program.
    """
    def __init__(self, port, baud_rate):
        # Open the serial port
        self.ser = serial.Serial(port, baud_rate)
        self.ser.flushInput()  # Flush the serial input buffer

        # Queue to hold the data from the serial port
        self.data_queue = Queue()

        # Flag to stop the data reading thread
        self.stop_thread = False

        # Start the data reading thread
        self.thread = Thread(target=self.read_from_serial)
        self.thread.start()

    def read_from_serial(self):
        """
        This method runs continuously in a separate thread
        to read data from the serial port and add it to the queue.
        """
        while not self.stop_thread:
            try:
                if self.ser.inWaiting():
                    # Read a line of text from the serial port
                    line = self.ser.readline().decode("utf-8").strip()

                    # Split the line into timestamp and data value
                    timestamp, value = map(float, line.split(","))

                    # Add the data to the queue
                    self.data_queue.put((timestamp, value))
            except (OSError, serial.SerialException):
                print("Error reading from serial port")
                break
            except ValueError:
                print(f"Received invalid data: {line}")  # Print the received data

    def stop(self):
        """
        This method stops the serial reader and cleans up.
        """
        self.stop_thread = True
        self.thread.join()
        self.ser.close()


class DataPlotter:
    """
    This class plots the data from the Arduino in real time.
    It pulls the data from the queue and plots it.
    """
    def __init__(self, reader, plot_window=500):
        self.reader = reader
        self.plot_window = plot_window

        # Lists to hold the time and data values
        self.time_data = []
        self.value_data = []

        # Create the PyQt application
        self.app = QApplication([])

        # Create the PyQtGraph window
        self.win = pg.GraphicsLayoutWidget()  
        self.win.setWindowTitle('Realtime plot')
        self.win.show()  # Show the window

        # Add a plot to the window
        self.plot = self.win.addPlot(title="EMG Data")

        # Add a curve to the plot
        self.curve = self.plot.plot(pen='y')

        # Create a PyQt timer. This will call the update function at the specified interval
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):
        """
        This method is called every time the timer 'ticks'.
        It pulls the data from the queue and plots it.
        """
        while not self.reader.data_queue.empty():
            # Get the newest data from the queue
            timestamp, value = self.reader.data_queue.get()

            # Add the new data to the lists
            self.time_data.append(timestamp)
            self.value_data.append(value)

            # Ensure the lists don't grow larger than the specified window
            self.time_data = self.time_data[-self.plot_window:]
            self.value_data = self.value_data[-self.plot_window:]

            # Update the plotted data
            self.curve.setData(self.time_data, self.value_data)

    def start(self):
        """
        This method starts the PyQt event loop.
        It will not return until the application exits.
        """
        self.app.aboutToQuit.connect(self.reader.stop)  # Connect the exit signal to the stop method of the reader
        QApplication.instance().exec_()

if __name__ == "__main__":
    # Create an instance of the SerialReader class with the specified port and baud rate
    reader = SerialReader('COM5', 115200)

    # Create an instance of the DataPlotter class, using the reader and a plot window of 500 data points
    plotter = DataPlotter(reader)

    # Start the plotter
    plotter.start()
