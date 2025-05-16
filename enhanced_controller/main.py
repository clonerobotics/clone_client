# enhanced_controller/main.py

from control.hand_controller import HandController
from interface.hand_gui import HandGUI
from interface.feedback_panel import FeedbackPanel
from data.motion_logger import MotionLogger
from intelligence.motion_annotator import MotionAnnotator

def main():
    logger = MotionLogger()
    controller = HandController(logger=logger)
    gui = HandGUI(controller)
    feedback = FeedbackPanel(controller)
    annotator = MotionAnnotator(logger)

    print("[System] Launching enhanced controller...")
    gui.run()
    feedback.listen()
    annotator.monitor()

if __name__ == "__main__":
    main()
