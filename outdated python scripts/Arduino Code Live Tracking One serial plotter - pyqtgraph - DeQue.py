import serial
from threading import Thread
from queue import Queue
import pyqtgraph as pg
from pyqtgraph.Qt.QtWidgets import QApplication
from pyqtgraph.Qt import QtCore
from collections import deque
import traceback

class SerialReader:
    """
    A class used to continuously read from a serial port in a separate thread.
    The data is stored in a queue for consumption.
    """
    def __init__(self, port, baud_rate):
        """
        Initialize SerialReader with specified port and baud_rate.
        Start the thread that reads from the serial port.

        :param port: The serial port to read from.
        :param baud_rate: The baud rate for the serial communication.
        """

        self.ser = serial.Serial(port, baud_rate)
        self.ser.flushInput()
        self.data_queue = Queue()
        self.stop_thread = False
        self.thread = Thread(target=self.read_from_serial)
        self.thread.start()

    def read_from_serial(self):
        """
        Continuously read lines from the serial port, parse them, and put them in the queue.
        Stop if stop_thread is set to True or an error occurs.
        """
        while not self.stop_thread:
            try:
                if self.ser.inWaiting():
                    line = self.ser.readline().decode("utf-8").strip()
                    timestamp, value = map(float, line.split(","))
                    self.data_queue.put((timestamp, value))
            except (OSError, serial.SerialException) as e:
                print("Error reading from serial port")
                print(traceback.format_exc())
                break
            except ValueError as e:
                print(f"Received invalid data: {line}")
                print(traceback.format_exc())

    def stop(self):
        """
        Stop the reading thread and close the serial port.
        """
        self.stop_thread = True
        self.thread.join()
        self.ser.close()


class DataPlotter:
    """
    A class used to plot data in real time from a SerialReader.
    """
    def __init__(self, reader, plot_window=500):
        """
        Initialize DataPlotter with a SerialReader and set up the plot.

        :param reader: The SerialReader to get data from.
        :param plot_window: The number of data points to keep on the plot.
        """
        self.reader = reader
        self.time_data = deque(maxlen=plot_window)
        self.value_data = deque(maxlen=plot_window)
        self.setup_plot()

    def setup_plot(self):
        """
        Set up the PyQtGraph plot.
        """
        self.app = QApplication([])
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle('Realtime plot')
        self.win.show()
        self.plot = self.win.addPlot(title="EMG Data")
        self.curve = self.plot.plot(pen='y')
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def update(self):
        """
        Update the plot with new data from the SerialReader.
        """
        while not self.reader.data_queue.empty():
            timestamp, value = self.reader.data_queue.get()
            self.time_data.append(timestamp)
            self.value_data.append(value)
            self.curve.setData(self.time_data, self.value_data)

    def start(self):
        """
        Start the PyQt application. This method will not return until the application exits.
        """
        self.app.aboutToQuit.connect(self.reader.stop)  # Ensure reader is stopped when application exits
        QApplication.instance().exec_()

if __name__ == "__main__":
    """
    When script is run directly, create a SerialReader for 'COM5' at 115200 baud,
    and a DataPlotter to plot the data. Start the DataPlotter.
    """
    reader = SerialReader('COM5', 115200)
    plotter = DataPlotter(reader)
    plotter.start()
