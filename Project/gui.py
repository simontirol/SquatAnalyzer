import tkinter as tk
from tkinter import ttk

def create_gui(start_measurement_callback, stop_measurement_callback):
    root = tk.Tk()
    root.title("Squat Analysis Dashboard")
    root.geometry("800x600")  # Adjusted to fit the video feed

    # Start/Stop Buttons
    start_button = ttk.Button(root, text="Start Measurement", command=start_measurement_callback)
    start_button.pack(pady=10)

    stop_button = ttk.Button(root, text="Stop Measurement", command=stop_measurement_callback)
    stop_button.pack(pady=10)

    # Labels for angles
    knee_angle_label = ttk.Label(root, text="Knee Angle: N/A")
    knee_angle_label.pack(pady=10)

    femur_angle_label = ttk.Label(root, text="Femur Angle: N/A")
    femur_angle_label.pack(pady=10)

    # Canvas to show live video feed
    video_canvas = tk.Canvas(root, width=640, height=480)
    video_canvas.pack()

    return root, knee_angle_label, femur_angle_label, video_canvas



