# enhanced_controller/controller.py

from enhanced_controller.hardware.hardware_adapter import HardwareAdapter

class EnhancedController:
    def __init__(self):
        self.hardware = HardwareAdapter()

    def move_all_fingers(self, angles):
        for finger, angle in angles.items():
            self.hardware.set_finger_angle(finger, angle)

    def perform_grip_sequence(self):
        # Example grip sequence with predefined angles
        sequence = [
            {'thumb': 45, 'index': 90, 'middle': 90, 'ring': 90, 'pinky': 90},
            {'thumb': 30, 'index': 60, 'middle': 60, 'ring': 60, 'pinky': 60},
            {'thumb': 0,  'index': 0,  'middle': 0,  'ring': 0,  'pinky': 0}
        ]
        for step in sequence:
            self.move_all_fingers(step)

    def relax_hand(self):
        self.hardware.relax()
