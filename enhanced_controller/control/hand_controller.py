# enhanced_controller/control/hand_controller.py

import time
from interface.hardware_adapter import HardwareAdapter

class HandController:
    def __init__(self, logger=None):
        self.hardware = HardwareAdapter()
        self.logger = logger

    def move_finger(self, finger_name: str, angle: float):
        self.hardware.set_finger_angle(finger_name, angle)
        if self.logger:
            self.logger.log(f"Moved {finger_name} to {angle} degrees")

    def move_all_fingers(self, angles: dict):
        for finger, angle in angles.items():
            self.move_finger(finger, angle)

    def relax_hand(self):
        self.hardware.relax()
        if self.logger:
            self.logger.log("Hand relaxed")

    def perform_grip_sequence(self):
        grip_pattern = {
            'thumb': 60,
            'index': 90,
            'middle': 90,
            'ring': 80,
            'pinky': 75
        }
        self.move_all_fingers(grip_pattern)
        time.sleep(0.5)
        self.relax_hand()
