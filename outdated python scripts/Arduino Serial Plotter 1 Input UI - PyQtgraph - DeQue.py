import serial
from threading import Thread, Lock
from queue import Queue
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLineEdit, QLabel, QWidget
from pyqtgraph.Qt import QtCore
from collections import deque
import traceback
import os
import pandas as pd

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
    A class used to plot data in real time from a SerialReader and allow for recording of gestures.
    """
    def __init__(self, reader, plot_window=500):
        """
        Initialize DataPlotter with a SerialReader and set up the plot and UI.

        :param reader: The SerialReader to get data from.
        :param plot_window: The number of data points to keep on the plot.
        """
        self.reader = reader
        self.time_data = deque(maxlen=plot_window)
        self.value_data = deque(maxlen=plot_window)
        self.record_data = []
        self.record_lock = Lock()  # Use a lock for thread-safe recording
        self.is_recording = False
        self.setup_ui()
        self.setup_plot()

        # Connect aboutToQuit to stop
        QApplication.instance().aboutToQuit.connect(self.reader.stop)

    def setup_ui(self):
        """
        Set up the user interface with a button and a line edit for file naming.
        """
        self.app = QApplication([])
        # Create container widget first and set layout
        self.container = QWidget()
        layout = QVBoxLayout()
        self.container.setLayout(layout)

        # Create graphics layout widget
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle('Realtime plot')
        layout.addWidget(self.win)  # Add it to the layout here

        # Create widgets
        self.record_button = QPushButton('Record Gesture')
        self.file_name_edit = QLineEdit()
        self.label = QLabel('Enter file title:')

        # Add widgets to layout
        layout.addWidget(self.record_button)
        layout.addWidget(self.label)
        layout.addWidget(self.file_name_edit)
        
        self.container.show()  # Show the container widget

        # Connect button click to handler
        self.record_button.clicked.connect(self.record_gesture)

    def setup_plot(self):
        """
        Set up the PyQtGraph plot.
        """
        self.plot = self.win.addPlot(title="EMG Data")
        self.curve = self.plot.plot(pen='y')
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def start_countdown(self):
        """
        Start a countdown before recording.
        """
        self.label.setText('Recording will start in 3 seconds...')
        QtCore.QTimer.singleShot(3000, self.start_recording)

    def record_gesture(self):
        """
        Handle click on "Record Gesture" button.
        Start 3 second countdown, then record for 5 seconds.
        """
        self.record_button.setEnabled(False)
        with self.record_lock:
            self.record_data = []  # Reset recording data
        self.start_countdown()

    def start_recording(self):
        """
        Start recording and set timer to stop recording after 5 seconds.
        """
        self.label.setText('Recording...')
        self.is_recording = True
        QtCore.QTimer.singleShot(5000, self.stop_recording)

    def stop_recording(self):
        """
        Stop recording, save data to CSV file and re-enable button.
        """
        self.is_recording = False
        file_title = self.file_name_edit.text()
        if file_title:
            file_path = os.path.join('output', 'gesture recordings', f'{file_title}.csv')
            with self.record_lock:
                df = pd.DataFrame(self.record_data, columns=['timestamp', 'value'])
            df.to_csv(file_path, index=False)
            self.label.setText(f'Saved recording as {file_title}.csv')
        else:
            self.label.setText('Recording completed, but no file title was entered. Data was not saved.')
        self.record_button.setEnabled(True)

    def update(self):
        """
        Update the plot with new data from the SerialReader and record if necessary.
        """
        while not self.reader.data_queue.empty():
            timestamp, value = self.reader.data_queue.get()
            self.time_data.append(timestamp)
            self.value_data.append(value)
            if self.is_recording:
                with self.record_lock:
                    self.record_data.append((timestamp, value))
            self.curve.setData(self.time_data, self.value_data)

    def start(self):
        """
        Start the Qt event loop.
        """
        QApplication.instance().exec_()


if __name__ == "__main__":
    """
    When script is run directly, create a SerialReader for 'COM5' at 115200 baud,
    and a DataPlotter to plot the data. Start the DataPlotter.
    """
    reader = SerialReader('COM5', 115200)
    plotter = DataPlotter(reader)
    plotter.start()
