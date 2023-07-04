import sys
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
from scipy.signal import butter, filtfilt

# Variables to adjust filter parameters
FS = 1000  # Sample rate
CUTOFF_HIGH = 10  # High-pass filter cutoff frequency
CUTOFF_LOW = 50  # Low-pass filter cutoff frequency
CUTOFFS_MULTI = [10, 50]  # Multistage filter cutoff frequencies
ORDER = 5  # Filter order

# Function to design a Nth order Butterworth filter and return the filter coefficients.
def butter_filter(order, cutoff, fs, filter_type):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype=filter_type, analog=False)
    return b, a

# Function to apply filter.
def apply_filter(data, order, cutoff, fs, filter_type):
    b, a = butter_filter(order, cutoff, fs, filter_type)
    y = filtfilt(b, a, data)
    return y

# Low-pass filter
def lowpass_filter(data):
    return apply_filter(data, ORDER, CUTOFF_LOW, FS, 'low')

# High-pass filter
def highpass_filter(data):
    return apply_filter(data, ORDER, CUTOFF_HIGH, FS, 'high')

# Multi-stage filter
def multistage_filter(data):
    for cutoff in CUTOFFS_MULTI:
        data = apply_filter(data, ORDER, cutoff, FS, 'low')
    return data

# Comb filter
def comb_filter(buffer: np.array, delay: int = 24, alpha: float = 1.0) -> float:
    delayed_data = np.roll(buffer, delay)
    delayed_data[:delay] = 0
    y = buffer - alpha * delayed_data
    return y[-1]  # return only the last value

# Other constants in your script
BUFFER_SIZE = 1024  # Buffer size for serial port reading
RECORD_DELAY = 3000  # Delay before recording starts (ms)
RECORD_DURATION = 5000  # Duration of recording (ms)
sensor_placement_dict = {1: "Outer forearm sensor value (1)", 2: "Inner forearm sensor value (2)"}  # ! Update if more sensors are added

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class SerialReader:
    def __init__(self, port: str, baud_rate: int, num_sensors: int) -> None:
        self.ser = serial.Serial(port, baud_rate)
        self.ser.flushInput()
        self.data_queue = Queue()
        self.stop_thread = False
        self.num_sensors = num_sensors
        self.thread = Thread(target=self.read_from_serial)
        self.thread.start()

    def read_from_serial(self) -> None:
        while not self.stop_thread:
            try:
                if self.ser.inWaiting():
                    line = self.ser.readline().decode("utf-8").strip()
                    if not line:
                        continue
                    data = list(map(float, line.split(",")))
                    if len(data) != self.num_sensors + 1:  # expect timestamp + n sensor values
                        raise ValueError
                    self.data_queue.put(data)
            except (OSError, serial.SerialException) as e:
                logging.error("Error reading from serial port", exc_info=True)
                break
            except ValueError as e:
                logging.error(f"Received invalid data: {line}", exc_info=True)

    def stop(self) -> None:
        self.stop_thread = True
        if self.thread.is_alive():
            self.thread.join()
        self.ser.close()


class DataPlotter:
    def __init__(self, reader: SerialReader, plot_window: int = 500) -> None:
        self.reader = reader
        self.time_data = np.zeros(plot_window)
        self.value_data = [np.zeros(plot_window) for _ in range(reader.num_sensors)]
        self.record_data = []
        self.record_lock = Lock()
        self.is_recording = False
        self.is_auto_scaled = True
        self.buffer_size = 128
        self.buffer = [np.zeros(self.buffer_size) for _ in range(reader.num_sensors)]  # Added buffer for filter
        self.setup_ui()
        self.setup_plot()
        QApplication.instance().aboutToQuit.connect(self.reader.stop)

    def setup_ui(self) -> None:
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
        self.plot = [self.win.addPlot(title=sensor_placement_dict[i + 1] + " data") for i in range(self.reader.num_sensors)]
        self.curve = [p.plot(pen='y') for p in self.plot]
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def start_countdown(self) -> None:
        self.label.setText('Recording will start in 3 seconds...')
        QtCore.QTimer.singleShot(RECORD_DELAY, self.start_recording)

    def record_gesture(self) -> None:
        self.record_button.setEnabled(False)
        with self.record_lock:
            self.record_data = []
        self.start_countdown()

    def start_recording(self) -> None:
        self.label.setText('Recording...')
        self.is_recording = True
        QtCore.QTimer.singleShot(RECORD_DURATION, self.stop_recording)

    def stop_recording(self) -> None:
        self.is_recording = False
        file_title = self.file_name_edit.text()
        if file_title:
            file_path = os.path.join('output', 'gesture recordings', f'{file_title}.csv')
            with self.record_lock:
                df = pd.DataFrame(self.record_data, columns=['timestamp'] + [sensor_placement_dict[i + 1] for i in range(self.reader.num_sensors)])
            df.to_csv(file_path, index=False, chunksize=1000)
            self.label.setText(f'Saved recording as {file_title}.csv')
        else:
            self.label.setText('Recording completed, but no file title was entered. Data was not saved.')
        self.record_button.setEnabled(True)

    def toggle_y_axis(self) -> None:
        if self.is_auto_scaled:
            for p in self.plot:
                p.setYRange(-500, 500, padding=0)
        else:
            for p in self.plot:
                p.enableAutoRange('y', True)
        self.is_auto_scaled = not self.is_auto_scaled

    def update(self) -> None:
        while not self.reader.data_queue.empty():
            data = self.reader.data_queue.get()
            self.time_data[:-1] = self.time_data[1:]
            self.time_data[-1] = data[0]
            for i, val in enumerate(data[1:]):
                self.buffer[i][:-1] = self.buffer[i][1:]  # shift buffer values to the left
                self.buffer[i][-1] = val  # add new sensor value to buffer

                filtered_value = comb_filter(self.buffer[i])  # apply comb filter
                filtered_value = lowpass_filter(filtered_value)  # apply low-pass filter
                filtered_value = highpass_filter(filtered_value)  # apply high-pass filter
                filtered_value = multistage_filter(filtered_value)  # apply multi-stage filter

                self.value_data[i][:-1] = self.value_data[i][1:]
                self.value_data[i][-1] = filtered_value

                if self.is_recording:
                    with self.record_lock:
                        self.record_data.append([data[0]] + [self.value_data[j][-1] for j in range(self.reader.num_sensors)])

        for i, c in enumerate(self.curve):
            c.setData(self.time_data, self.value_data[i])


if __name__ == "__main__":
    reader = SerialReader(port='COM5', baud_rate=115200, num_sensors=2)
    plotter = DataPlotter(reader)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()