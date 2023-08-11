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
from pynput import mouse

# ! Good values for alpha:0.5, Delay: 13/25/37 (roughly), Gain: 1.0

NUM_OF_SENSORS = 2  # ! Number of sensors - check main.cpp for number expected
BUFFER_SIZE = 1024  # Buffer size for serial port reading
RECORD_DELAY = 3000  # Delay before recording starts (ms)
RECORD_DURATION = 600000  # Duration of recording (ms)

sensor_placement_dict = {1:"Outer forearm sensor value (1)", 2: "Inner forearm sensor value (2)"} # ! Update if more sensors are added

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class MouseListener:
    def __init__(self, data_plotter):
        self.data_plotter = data_plotter
        self.left_state = 0
        self.right_state = 0
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

    def on_click(self, x, y, button, pressed):
        if button == mouse.Button.left:
            self.left_state = int(pressed)
        elif button == mouse.Button.right:
            self.right_state = int(pressed)

class LowPassFilter:
    def __init__(self, alpha: float):
        self.alpha = alpha
        self.state = 0

    def filter(self, value: float) -> float:
        self.state = self.alpha * value + (1 - self.alpha) * self.state
        return self.state

class HighPassFilter:
    def __init__(self, alpha: float):
        self.alpha = alpha
        self.low_pass_filter = LowPassFilter(alpha)
        self.prev_raw_value = None
        self.prev_high_passed_value = 0

    def filter(self, value: float) -> float:
        if self.prev_raw_value is None:
            self.prev_raw_value = value
        high_passed_value = self.alpha * self.prev_high_passed_value + self.alpha * (value - self.prev_raw_value)
        self.prev_raw_value = value
        self.prev_high_passed_value = high_passed_value
        return high_passed_value

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
        self.alpha = 0.1
        self.comb_filters = [CombFilter(delay=0, gain=0) for _ in range(reader.NUM_OF_SENSORS)]
        self.low_pass_filters = [LowPassFilter(alpha=self.alpha) for _ in range(reader.NUM_OF_SENSORS)]
        self.high_pass_filters = [HighPassFilter(alpha=self.alpha) for _ in range(reader.NUM_OF_SENSORS)]
        self.setup_ui()
        self.setup_plot()
        QApplication.instance().aboutToQuit.connect(self.reader.stop)
        self.filters_enabled = True
        self.mouse_left_data = np.zeros(plot_window)
        self.mouse_right_data = np.zeros(plot_window)


    def toggle_filters(self):
        self.filters_enabled = self.enable_filters_button.isChecked()
        self.enable_filters_button.setText('Enable Filters' if not self.filters_enabled else 'Disable Filters')

    def setup_ui(self) -> None:
        self.app = QApplication([])
        self.container = QWidget()
        layout = QVBoxLayout()
        self.container.setLayout(layout)
        self.win = pg.GraphicsLayoutWidget()
        self.win.setWindowTitle('Realtime plot')
        layout.addWidget(self.win)

        # add the sensor plots to the first row
        self.plot = [self.win.addPlot(row=0, col=i, title=f"{sensor_placement_dict[i+1]} data") for i in range(reader.NUM_OF_SENSORS)]
        self.curve = [p.plot(pen='y') for p in self.plot]

        # Add the mouse button plots to the second row
        self.mouse_left_plot = self.win.addPlot(row=1, col=0, title='Left Mouse Button State')
        self.mouse_left_curve = self.mouse_left_plot.plot(pen='y')
        self.mouse_left_plot.setYRange(0, 1)  # Set fixed y-axis range for left mouse button plot

        self.mouse_right_plot = self.win.addPlot(row=1, col=1, title='Right Mouse Button State')
        self.mouse_right_curve = self.mouse_right_plot.plot(pen='y')
        self.mouse_right_plot.setYRange(0, 1)  # Set fixed y-axis range for right mouse button plot


        self.enable_filters_button = QPushButton('Enable Filters')
        self.enable_filters_button.setCheckable(True)
        self.enable_filters_button.toggle()  # Filters are enabled by default
        self.container.layout().addWidget(self.enable_filters_button)
        self.enable_filters_button.clicked.connect(self.toggle_filters)


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

        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(100)
        self.alpha_slider.setValue(int(self.alpha * 100))
        self.alpha_label = QLabel(f'Alpha: {self.alpha}')
        self.alpha_slider.valueChanged.connect(self.update_alpha)

        layout.addWidget(self.alpha_slider)
        layout.addWidget(self.alpha_label)

        # self.mouse_left_plot = self.win.addPlot(title='Left Mouse Button State')
        # self.mouse_left_curve = self.mouse_left_plot.plot(pen='y')
        # self.mouse_right_plot = self.win.addPlot(title='Right Mouse Button State')
        # self.mouse_right_curve = self.mouse_right_plot.plot(pen='y')

        self.container.show()

    def update_alpha(self, value):
        self.alpha = value / 100.0
        self.alpha_label.setText(f"Alpha: {self.alpha}")
        for lp_filter in self.low_pass_filters:
            lp_filter.alpha = self.alpha
        for hp_filter in self.high_pass_filters:
            hp_filter.alpha = self.alpha

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
        # self.plot = [self.win.addPlot(title=f"{sensor_placement_dict[i+1]} data") for i in range(self.reader.NUM_OF_SENSORS)]
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
                df = pd.DataFrame(self.record_data, columns=['timestamp'] + [sensor_placement_dict[i+1] for i in range(self.reader.NUM_OF_SENSORS)] + ['left mouse button', 'right mouse button'])
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

            # Shift and append the current mouse states to the mouse state data arrays
            self.mouse_left_data = self.shift_and_append(self.mouse_left_data, self.mouse_listener.left_state)
            self.mouse_right_data = self.shift_and_append(self.mouse_right_data, self.mouse_listener.right_state)

            if self.is_recording:
                with self.record_lock:
                    # Include mouse button states in the recorded data
                    self.record_data.append([self.time_data[-1]] + [self.value_data[j][-1] for j in range(self.reader.NUM_OF_SENSORS)] + [self.mouse_left_data[-1], self.mouse_right_data[-1]])
            for i, value in enumerate(data[1:]):
                if self.filters_enabled:
                    value = self.comb_filters[i].filter(value)  # Apply Comb filter
                    value = self.low_pass_filters[i].filter(value)  # Apply Low Pass filter
                    value = self.high_pass_filters[i].filter(value)  # Apply High Pass filter
                self.value_data[i] = self.shift_and_append(self.value_data[i], value)
                self.curve[i].setData(self.time_data, self.value_data[i])

            # Update the mouse button plots
            self.mouse_left_curve.setData(self.time_data, self.mouse_left_data)
            self.mouse_right_curve.setData(self.time_data, self.mouse_right_data)

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

        mouse_listener = MouseListener(plotter)  # Create the mouse listener

        plotter.mouse_listener = mouse_listener  # Add the mouse listener to the plotter

        plotter.start()

    except ValueError as e:
        print(e)