import sys
import time
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
import collections
import multiprocessing
import queue

# ! This currently has some issues
# ! 1. The state posting is not working correctly - rest state is not being posted correctly
# ! 2. The data being captured has some issues - there is a couple microseconds of delay roughly every 0.5 seconds, assumed to be due to the serial port reading

BUFFER_SIZE = 1024  # Buffer size for serial port reading
RECORD_DELAY = 3000  # Delay before recording starts (ms)
RECORD_DURATION = 5000  # Duration of recording (ms)



sensor_placement_dict = {1:"Outer forearm sensor value (1)", 2: "Inner forearm sensor value (2)"} # ! Update if more sensors are added

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class SerialReader:
    def __init__(self, port: str, baud_rate: int, num_sensors: int) -> None:
        self.ser = serial.Serial(port, baud_rate)
        self.ser.flushInput()
        self.data_queue = multiprocessing.Queue()
        # self.data_queue = Queue()
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


class ThresholdNotifier:
    def __init__(self, port: str, baud_rate: int, num_sensors: int, delay: float = 0.5, queue_size: int = 20) -> None:
        self.port = port
        self.baud_rate = baud_rate
        self.num_sensors = num_sensors
        self.delay = delay
        self.stop_thread = False
        self.value_queues = [collections.deque(maxlen=queue_size) for _ in range(num_sensors)]
        self.thread = multiprocessing.Process(target=self.check_conditions)
        self.thread.start()

    def check_conditions(self) -> None:
        reader = SerialReader(self.port, self.baud_rate, self.num_sensors)
        while not reader.stop_thread:
            while not self.reader.data_queue.empty():
                data = self.reader.data_queue.get()
                for i, value in enumerate(data[1:]):
                    self.value_queues[i].append(value)
            self.evaluate_queues()
            time.sleep(self.delay)

    def evaluate_queues(self) -> None:
        inner_sensor_values = list(self.value_queues[1])
        outer_sensor_values = list(self.value_queues[0])

        if len(inner_sensor_values) < 20 or len(outer_sensor_values) < 20:  # not enough data yet
            return

        inner_disconnected = sum(1 for v in inner_sensor_values if v < 50 or v > 600) >= 15
        outer_disconnected = sum(1 for v in outer_sensor_values if v < 50 or v > 600) >= 15

        if inner_disconnected and outer_disconnected:
            print("Both sensors disconnected")
            return
        elif inner_disconnected:
            print("Inner sensor disconnected")
            return
        elif outer_disconnected:
            print("Outer sensor disconnected")
            return
        
        if all(300 <= v <= 400 for v in inner_sensor_values) and all(300 <= v <= 400 for v in outer_sensor_values):
            print("Rest")
            return

        # Conditions for "extension"
        if all(0 <= v <= 659 for v in outer_sensor_values) and all(275 <= v <= 425 for v in inner_sensor_values):
            print("Extension")
            return

        # Conditions for "flexion"
        if all(0 <= v <= 659 for v in inner_sensor_values) and all(275 <= v <= 425 for v in outer_sensor_values):
            print("Flexion")
            return

        # None of the conditions were met
        print("Bad reading")

    def stop(self) -> None:
        self.stop_thread = True
        if self.thread.is_alive():
            self.thread.join()


class DataPlotter:
    def __init__(self, reader: SerialReader, plot_window: int = 500) -> None:
        self.reader = reader
        self.time_data = np.zeros(plot_window)
        self.value_data = [np.zeros(plot_window) for _ in range(reader.num_sensors)]
        self.record_data = []
        self.record_lock = Lock()
        self.is_recording = False
        self.is_auto_scaled = True
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
        self.plot = [self.win.addPlot(title = sensor_placement_dict[i+1] + " data") for i in range(self.reader.num_sensors)]
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
                df = pd.DataFrame(self.record_data, columns=['timestamp'] + [sensor_placement_dict[i+1] for i in range(self.reader.num_sensors)])
            df.to_csv(file_path, index=False, chunksize=1000)
            self.label.setText(f'Saved recording as {file_title}.csv')
        else:
            self.label.setText('Recording completed, but no file title was entered. Data was not saved.')
        self.record_button.setEnabled(True)

    def toggle_y_axis(self) -> None:
        if self.is_auto_scaled:
            for p in self.plot:
                p.setYRange(min=-50, max=700)
            self.is_auto_scaled = False
        else:
            for p in self.plot:
                p.enableAutoRange(axis='y')
            self.is_auto_scaled = True

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
                self.value_data[i] = self.shift_and_append(self.value_data[i], value)
                self.curve[i].setData(self.time_data, self.value_data[i])

    def start(self) -> None:
        multiprocessing.Process(target=QApplication.instance().exec_).start()
        # QApplication.instance().exec_()

port = 'COM5'
baud_rate = 115200
num_sensors = 2

reader = SerialReader(port, baud_rate, num_sensors)
notifier = ThresholdNotifier(port, baud_rate, num_sensors)
plotter = DataPlotter(reader)
plotter.start()
notifier.stop()  # stop notifier when done

def run_qt_app():
    app = QApplication(sys.argv)
    plotter = Plotter()
    plotter.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    multiprocessing.Process(target=run_qt_app).start()



