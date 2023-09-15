
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtCore import QTimer
from final_serial_communication import SerialReader
from final_filtering import LowPassFilter, HighPassFilter, CombFilter

class DataPlotter(QMainWindow):
    def __init__(self, reader: SerialReader, plot_window: int = 500):
        super(DataPlotter, self).__init__()
        self.reader = reader
        self.plot_window = plot_window

        # Set up the main window layout and UI components
        self.setWindowTitle("EMG Data Visualization")
        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)
        
        # Placeholder for the plot widget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        self.plot_data = self.plot_widget.plot([], pen='y')
        
        self.start_button = QPushButton("Start")
        self.layout.addWidget(self.start_button)
        self.start_button.clicked.connect(self.start_plotting)
        
        self.stop_button = QPushButton("Stop")
        self.layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop_plotting)
        
        self.setLayout(self.layout)

        # Timer to update the plots periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plots)

    def start_plotting(self):
        self.timer.start(100)  # update every 100ms

    def stop_plotting(self):
        self.timer.stop()

    def update_plots(self):
        data = list(self.reader.data_queue)
        if data:
            timestamps = [entry[0] for entry in data]
            values = [entry[1:] for entry in data]  # Assuming multiple sensor values can be plotted
            self.plot_data.setData(timestamps, values)

def start_data_plotting():
    app = QApplication([])
    reader = SerialReader(port="COM3", baud_rate=9600, NUM_OF_SENSORS=2)  # Placeholder values
    plotter = DataPlotter(reader)
    plotter.show()
    app.exec_()

