# enhanced_controller/utils/motion_range.py

class MotionRange:
    # Based on anatomical range limits inspired by classical human motion studies
    RANGE_LIMITS = {
        'thumb': (0, 90),
        'index': (0, 110),
        'middle': (0, 110),
        'ring': (0, 110),
        'pinky': (0, 90)
    }

    @staticmethod
    def clamp_motion(finger: str, angle: float) -> float:
        min_angle, max_angle = MotionRange.RANGE_LIMITS.get(finger, (0, 90))
        return max(min_angle, min(angle, max_angle))
