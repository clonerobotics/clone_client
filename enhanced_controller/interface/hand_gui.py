# enhanced_controller/interface/hand_gui.py

import tkinter as tk
from tkinter import ttk

class HandGUI:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Clone Hand Controller")

        self.angle_vars = {
            'thumb': tk.DoubleVar(value=0),
            'index': tk.DoubleVar(value=0),
            'middle': tk.DoubleVar(value=0),
            'ring': tk.DoubleVar(value=0),
            'pinky': tk.DoubleVar(value=0),
        }

        self.build_ui()

    def build_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()

        row = 0
        for finger, var in self.angle_vars.items():
            ttk.Label(frame, text=finger.capitalize()).grid(column=0, row=row)
            slider = ttk.Scale(frame, from_=0, to=120, variable=var, orient='horizontal')
            slider.grid(column=1, row=row)
            row += 1

        ttk.Button(frame, text="Move Fingers", command=self.move_fingers).grid(column=0, row=row, columnspan=2, pady=10)
        ttk.Button(frame, text="Grip Sequence", command=self.controller.perform_grip_sequence).grid(column=0, row=row+1, columnspan=2)
        ttk.Button(frame, text="Relax", command=self.controller.relax_hand).grid(column=0, row=row+2, columnspan=2, pady=5)

    def move_fingers(self):
        angles = {finger: var.get() for finger, var in self.angle_vars.items()}
        self.controller.move_all_fingers(angles)

    def run(self):
        self.root.mainloop()
