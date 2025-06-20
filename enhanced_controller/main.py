# enhanced_controller/main.py

from enhanced_controller.controller import EnhancedController
from enhanced_controller.sensors.touch_sensor import TouchSensor
from enhanced_controller.utils.motion_range import MotionRange
from enhanced_controller.data.motion_logger import MotionLogger
import time

def main():
    controller = EnhancedController()
    touch_sensor = TouchSensor()
    logger = MotionLogger()

    try:
        while True:
            touched = touch_sensor.read_touch()
            if touched:
                logger.log("Touch detected - initiating grip")
                grip_angles = {
                    'thumb': MotionRange.clamp_motion('thumb', 45),
                    'index': MotionRange.clamp_motion('index', 90),
                    'middle': MotionRange.clamp_motion('middle', 90),
                    'ring': MotionRange.clamp_motion('ring', 90),
                    'pinky': MotionRange.clamp_motion('pinky', 90)
                }
                controller.move_all_fingers(grip_angles)
            else:
                logger.log("No touch detected - relaxing hand")
                controller.relax_hand()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.log("Program terminated by user")

if __name__ == "__main__":
    main()
