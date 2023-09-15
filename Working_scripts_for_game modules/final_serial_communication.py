
import serial
import logging
import threading
from collections import deque
from typing import List, Optional

logging.basicConfig(level=logging.INFO)

class SerialReader:
    def __init__(self, port: str, baud_rate: int, NUM_OF_SENSORS: int):
        try:
            self.ser = serial.Serial(port, baud_rate, timeout=1)
            self.NUM_OF_SENSORS = NUM_OF_SENSORS
            self.data_queue = deque(maxlen=1000)  # Stores recent data for processing
            self.reading = True
            self.thread = threading.Thread(target=self.read_from_serial)
            self.thread.start()
            logging.info(f"Serial reader initialized on port {port} with baud rate {baud_rate}")
        except Exception as e:
            logging.error(f"Error initializing serial reader: {e}")
            raise

    def read_from_serial(self):
        while self.reading:
            try:
                if self.ser.in_waiting:
                    data = self.ser.readline().decode('utf-8').strip()
                    values = data.split(',')
                    if len(values) == self.NUM_OF_SENSORS + 1:  # 1 for the timestamp
                        self.data_queue.append(values)
            except Exception as e:
                logging.error(f"Error reading from serial: {e}")

    def stop(self):
        self.reading = False
        self.thread.join()
        self.ser.close()
        logging.info("Serial reader stopped")

# For now, using the placeholder function to find the COM port
# In an actual application, the pyserial library can be used to list available ports and select based on certain criteria
def find_com_port(vendor_id: Optional[int] = None, 
                  product_id: Optional[int] = None, 
                  device_description: Optional[str] = None) -> str:
    return "COM3"  # Placeholder

