# enhanced_controller/data/motion_logger.py

import csv
import datetime

class MotionLogger:
    def __init__(self, filename="motion_log.csv"):
        self.filename = filename
        self._initialize_file()

    def _initialize_file(self):
        try:
            with open(self.filename, mode='x', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'event'])
        except FileExistsError:
            pass

    def log(self, event: str):
        timestamp = datetime.datetime.now().isoformat()
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, event])
