import numpy as np
import serial
from threading import Thread, Lock
import pandas as pd
from queue import Queue
import os
import logging
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QLineEdit, QLabel, QWidget, QSlider, QSpinBox
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from collections import deque
from serial.tools import list_ports

NUM_OF_SENSORS = 2  # ! Number of sensors - check main.cpp for number expected
BUFFER_SIZE = 1024  # Buffer size for serial port reading
RECORD_DELAY = 3000  # Delay before recording starts (ms)
RECORD_DURATION = 5000  # Duration of recording (ms)

sensor_placement_dict = {1:"Outer forearm sensor value (1)", 2: "Inner forearm sensor value (2)"} # ! Update if more sensors are added

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class SerialReader:
    def __init__(self, port: str, baud_rate: int, NUM_OF_SENSORS: int) -> None:
        self.ser = serial.Serial(port, baud_rate)
        self.ser.flushInput()
        self.data_queue = Queue()
        self.stop_thread = False
        self.NUM_OF_SENSORS = NUM_OF_SENSORS
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
                    if len(data) != self.NUM_OF_SENSORS + 1:  # expect timestamp + n sensor values
                        raise ValueError(f"Received invalid data: {line}. Expected {self.NUM_OF_SENSORS + 1} values.")
                    self.data_queue.put(data)
            except (OSError, serial.SerialException) as e:
                logging.error("Error reading from serial port", exc_info=True)
                break
            except ValueError as e:
                logging.error(e, exc_info=True)

    def stop(self) -> None:
        self.stop_thread = True
        if self.thread.is_alive():
            self.thread.join()
        self.ser.close()

class CombFilter:
    def __init__(self, delay: int, gain: float) -> None:
        self.delay = delay
        self.gain = gain
        self.buffer = deque()

    def filter(self, signal: float) -> float:
        self.buffer.append(signal)
        if len(self.buffer) < self.delay:
            return signal
        else:
            output = signal - self.gain * self.buffer[-self.delay]
            self.buffer.popleft()  # remove oldest value
            return output
        
class DataPlotter:
    def __init__(self, reader: SerialReader, plot_window: int = 500) -> None:
        self.reader = reader
        self.time_data = np.zeros(plot_window)
        self.value_data = [np.zeros(plot_window) for _ in range(reader.NUM_OF_SENSORS)]
        self.record_data = []
        self.record_lock = Lock()
        self.is_recording = False
        self.is_auto_scaled = True
        self.comb_filters = [CombFilter(delay=0, gain=0) for _ in range(reader.NUM_OF_SENSORS)]
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

        # Adding QSpinBox for Y-axis positive height
        self.pos_y_axis_height = QSpinBox()
        self.pos_y_axis_height.setRange(1, 1000)
        self.pos_y_axis_height.setValue(700)  # default value

        # Adding QSpinBox for Y-axis negative height
        self.neg_y_axis_height = QSpinBox()
        self.neg_y_axis_height.setRange(-1000, -1)
        self.neg_y_axis_height.setValue(-50)  # default value

        self.container.layout().addWidget(QLabel('Positive Y-Axis Height:'))
        self.container.layout().addWidget(self.pos_y_axis_height)
        self.container.layout().addWidget(QLabel('Negative Y-Axis Height:'))
        self.container.layout().addWidget(self.neg_y_axis_height)

        self.delay_slider = QSlider(Qt.Horizontal)
        self.delay_slider.setMinimum(0)
        self.delay_slider.setMaximum(50)
        self.delay_label = QLabel('Delay: 0')
        self.delay_slider.valueChanged.connect(self.update_delay)

        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setMinimum(-100)
        self.gain_slider.setMaximum(100)
        self.gain_label = QLabel('Gain: 0')
        self.gain_slider.valueChanged.connect(self.update_gain)

        layout.addWidget(self.delay_slider)
        layout.addWidget(self.delay_label)
        layout.addWidget(self.gain_slider)
        layout.addWidget(self.gain_label)

        self.container.show()
        self.record_button.clicked.connect(self.record_gesture)
        self.toggle_y_axis_button.clicked.connect(self.toggle_y_axis)
        self.pos_y_axis_height.valueChanged.connect(self.update_y_range)
        self.neg_y_axis_height.valueChanged.connect(self.update_y_range)

    def update_y_range(self) -> None:
        if not self.is_auto_scaled:
            for p in self.plot:
                p.setYRange(min=self.neg_y_axis_height.value(), max=self.pos_y_axis_height.value())

    def toggle_y_axis(self) -> None:
        if self.is_auto_scaled:
            for p in self.plot:
                p.setYRange(min=self.neg_y_axis_height.value(), max=self.pos_y_axis_height.value())
            self.is_auto_scaled = False
        else:
            for p in self.plot:
                p.enableAutoRange(axis='y')
            self.is_auto_scaled = True

    def update_delay(self, value):
        value = int(value)
        self.delay_label.setText(f"Delay: {value}")
        for filter in self.comb_filters:
            filter.delay = value

    def update_gain(self, value):
        self.gain_label.setText(f"Gain: {value/100}")
        for filter in self.comb_filters:
            filter.gain = value / 100

    def setup_plot(self) -> None:
        self.plot = [self.win.addPlot(title=f"{sensor_placement_dict[i+1]} data") for i in range(self.reader.NUM_OF_SENSORS)]
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
                df = pd.DataFrame(self.record_data, columns=['timestamp'] + [sensor_placement_dict[i+1] for i in range(self.reader.NUM_OF_SENSORS)])
            df.to_csv(file_path, index=False, chunksize=1000)
            self.label.setText(f'Saved recording as {file_title}.csv')
        else:
            self.label.setText('Recording completed, but no file title was entered. Data was not saved.')
        self.record_button.setEnabled(True)

    def shift_and_append(self, data_array: np.array, new_value: float) -> np.array:
        data_array = np.roll(data_array, -1)
        data_array[-1] = new_value
        return data_array

    def update(self) -> None:
        while not self.reader.data_queue.empty():
            data = self.reader.data_queue.get()
            self.time_data = self.shift_and_append(self.time_data, data[0])
            if self.is_recording:
                with self.record_lock:
                    self.record_data.append(data)
            for i, value in enumerate(data[1:]):
                filtered_value = self.comb_filters[i].filter(value)  # Apply Comb filter
                self.value_data[i] = self.shift_and_append(self.value_data[i], filtered_value)
                self.curve[i].setData(self.time_data, self.value_data[i])

    def start(self) -> None:
        QApplication.instance().exec_()

def find_com_port(vendor_id=None, product_id=None, device_description=None):
    com_ports = list_ports.comports()

    for port in com_ports:
        if vendor_id and port.vid != vendor_id:
            continue
        if product_id and port.pid != product_id:
            continue
        if device_description and device_description not in port.description:
            continue
        return port.device

    raise ValueError("Device not found")

if __name__ == "__main__":
    try:
        port = find_com_port(device_description='Arduino')
        reader = SerialReader(port, 115200, NUM_OF_SENSORS)
        plotter = DataPlotter(reader)
        plotter.start()
    except ValueError as e:
        print(e)