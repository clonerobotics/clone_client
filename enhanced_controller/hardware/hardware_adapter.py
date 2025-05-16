# enhanced_controller/hardware/hardware_adapter.py

class HardwareAdapter:
    def __init__(self):
        # Initialize connection to hardware here
        pass

    def set_finger_angle(self, finger_name: str, angle: float):
        # Send command to hardware to set specific finger angle
        print(f"Setting {finger_name} angle to {angle} degrees")

    def relax(self):
        # Command hardware to relax all fingers
        print("Relaxing hand hardware")
