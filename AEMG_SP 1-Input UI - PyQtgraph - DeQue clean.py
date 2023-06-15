import numpy as np
import serial
from threading import Thread, Lock
import pandas as pd
from queue import Queue
import os
import logging
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLineEdit, QLabel, QWidget
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore

BUFFER_SIZE = 1024  # Buffer size for serial port reading
RECORD_DELAY = 3000  # Delay before recording starts (ms)
RECORD_DURATION = 5000  # Duration of recording (ms)

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class SerialReader:
    """
    A class used to continuously read from a serial port in a separate thread.
    The data is stored in a queue for consumption.
    """
    def __init__(self, port: str, baud_rate: int) -> None:
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

    def read_from_serial(self) -> None:
        """
        Continuously read lines from the serial port, parse them, and put them in the queue.
        Stop if stop_thread is set to True or an error occurs.
        """
        while not self.stop_thread:
            try:
                if self.ser.inWaiting():
                    line = self.ser.readline().decode("utf-8").strip()
                    if not line:
                        continue
                    timestamp, value = map(float, line.split(","))
                    self.data_queue.put((timestamp, value))
            except (OSError, serial.SerialException) as e:
                logging.error("Error reading from serial port", exc_info=True)
                break
            except ValueError as e:
                logging.error(f"Received invalid data: {line}", exc_info=True)

    def stop(self) -> None:
        """
        Stop the reading thread and close the serial port.
        """
        self.stop_thread = True
        if self.thread.is_alive():
            self.thread.join()
        self.ser.close()

class DataPlotter:
    """
    A class used to plot data in real time from a SerialReader and allow for recording of gestures.
    """
    def __init__(self, reader: SerialReader, plot_window: int = 500) -> None:
        """
        Initialize DataPlotter with a SerialReader and set up the plot and UI.

        :param reader: The SerialReader to get data from.
        :param plot_window: The number of data points to keep on the plot.
        """
        self.reader = reader
        self.time_data = np.zeros(plot_window)
        self.value_data = np.zeros(plot_window)
        self.record_data = []
        self.record_lock = Lock()
        self.is_recording = False
        self.is_auto_scaled = True
        self.setup_ui()
        self.setup_plot()

        # Connect aboutToQuit to stop
        QApplication.instance().aboutToQuit.connect(self.reader.stop)


    def setup_ui(self) -> None:
        """
        Set up the user interface with a button and a line edit for file naming.
        """
        self.app = QApplication([])
        self.container = QWidget()
        layout = QVBoxLayout()
        self.container.setLayout(layout)
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle('Realtime plot')
        layout.addWidget(self.win)
        self.record_button = QPushButton('Record Gesture')
        self.toggle_y_axis_button = QPushButton('Toggle Y-Axis Mode')
        self.file_name_edit = QLineEdit()
        self.label = QLabel('Enter file title:')
        self.container.layout().addWidget(self.label)
        self.container.layout().addWidget(self.file_name_edit)
        self.container.layout().addWidget(self.record_button)
        self.container.layout().addWidget(self.toggle_y_axis_button)
        self.container.show()
        self.record_button.clicked.connect(self.record_gesture)
        self.toggle_y_axis_button.clicked.connect(self.toggle_y_axis)

    def setup_plot(self) -> None:
        """
        Set up the PyQtGraph plot.
        """
        self.plot = self.win.addPlot(title="EMG Data")
        self.curve = self.plot.plot(pen='y')
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def start_countdown(self) -> None:
        """
        Start a countdown before recording.
        """
        self.label.setText('Recording will start in 3 seconds...')
        QtCore.QTimer.singleShot(RECORD_DELAY, self.start_recording)

    def record_gesture(self) -> None:
        """
        Handle click on "Record Gesture" button.
        Start 3 second countdown, then record for 5 seconds.
        """
        self.record_button.setEnabled(False)
        with self.record_lock:
            self.record_data = []  # Reset recording data
        self.start_countdown()

    def start_recording(self) -> None:
        """
        Start recording and set timer to stop recording after 5 seconds.
        """
        self.label.setText('Recording...')
        self.is_recording = True
        QtCore.QTimer.singleShot(RECORD_DURATION, self.stop_recording)

    def stop_recording(self) -> None:
        """
        Stop recording, save data to CSV file and re-enable button.
        """
        self.is_recording = False
        file_title = self.file_name_edit.text()
        if file_title:
            file_path = os.path.join('output', 'gesture recordings', f'{file_title}.csv')
            with self.record_lock:
                df = pd.DataFrame(self.record_data, columns=['timestamp', 'value'])
            df.to_csv(file_path, index=False, chunksize=1000)
            self.label.setText(f'Saved recording as {file_title}.csv')
        else:
            self.label.setText('Recording completed, but no file title was entered. Data was not saved.')
        self.record_button.setEnabled(True)

    def toggle_y_axis(self) -> None:
        """
        Handle click on "Toggle Y-Axis Mode" button.
        Switch between a static and auto-scaling range for the Y-axis on the plot.
        """
        if self.is_auto_scaled:
            self.plot.setYRange(min=0, max=800)
            self.is_auto_scaled = False
        else:
            self.plot.enableAutoRange(axis='y')
            self.is_auto_scaled = True

    def shift_and_append(self, data_array: np.array, new_value: float) -> np.array:
        data_array = np.roll(data_array, -1)
        data_array[-1] = new_value
        return data_array

    def update(self) -> None:
        """
        Update the plot with new data from the SerialReader and record if necessary.
        """
        while not self.reader.data_queue.empty():
            timestamp, value = self.reader.data_queue.get()
            self.time_data = self.shift_and_append(self.time_data, timestamp)
            self.value_data = self.shift_and_append(self.value_data, value)
            if self.is_recording:
                with self.record_lock:
                    self.record_data.append((timestamp, value))
            self.curve.setData(self.time_data, self.value_data)


    def start(self) -> None:
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
