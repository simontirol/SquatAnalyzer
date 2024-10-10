import cv2
import tkinter as tk
import numpy as np
from PIL import Image, ImageTk  # To handle image conversion for Tkinter
from aruco_detection import get_aruco_markers, draw_aruco_markers
from measurement import get_knee_angle, get_femur_angle
from gui import create_gui
import utils

class SquatAnalyzer:
    def __init__(self):
        self.cap = None
        self.knee_angle = 0
        self.femur_angle = 0
        self.is_measuring = False

    def start_measurement(self):
        self.cap = cv2.VideoCapture(0)  # Open the webcam
        self.is_measuring = True
        self.measure_loop()

    def stop_measurement(self):
        self.is_measuring = False
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

    def draw_lines_between_markers(self, frame, corners, ids):
        """Draw lines connecting the hip, knee, and ankle markers."""
        if ids is None:
            return frame  # No markers detected, return the original frame

        # Flatten ids array for easier lookup
        ids_flat = ids.flatten()

        # Check if the required markers (1, 2, 3) are detected
        if 1 in ids_flat and 2 in ids_flat and 3 in ids_flat:
            # Get the index of each marker
            hip_idx = list(ids_flat).index(1)
            knee_idx = list(ids_flat).index(2)
            ankle_idx = list(ids_flat).index(3)

            # Get the center positions of each marker by averaging their corner coordinates
            hip = np.mean(corners[hip_idx][0], axis=0).astype(int)  # Center of Marker 1 (hip)
            knee = np.mean(corners[knee_idx][0], axis=0).astype(int)  # Center of Marker 2 (knee)
            ankle = np.mean(corners[ankle_idx][0], axis=0).astype(int)  # Center of Marker 3 (ankle)

            # Draw a line from hip to knee
            cv2.line(frame, tuple(hip), tuple(knee), (0, 255, 0), 2)  # Green line for hip to knee
            # Draw a line from knee to ankle
            cv2.line(frame, tuple(knee), tuple(ankle), (0, 0, 255), 2)  # Red line for knee to ankle

        return frame

    def measure_loop(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame from camera.")
            return

        # Detect ArUco markers
        corners, ids = get_aruco_markers(frame)
        frame = draw_aruco_markers(frame, corners, ids)

        # Draw lines between hip, knee, and ankle markers
        frame = self.draw_lines_between_markers(frame, corners, ids)

        if corners is not None and len(corners) > 0:
            # Calculate knee and femur angles using the stable method
            self.knee_angle = get_knee_angle(corners, ids)
            self.femur_angle = get_femur_angle(corners, ids)

            # Update the GUI with the new angles
            if self.knee_angle is not None:
                knee_angle_label.config(text=f"Knee Angle: {self.knee_angle:.2f}")
            if self.femur_angle is not None:
                femur_angle_label.config(text=f"Femur Angle: {self.femur_angle:.2f}")

        # Convert the OpenCV frame (BGR) to an ImageTk (RGB) for Tkinter
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        imgtk = ImageTk.PhotoImage(image=img)

        # Update the canvas with the new frame
        video_canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        video_canvas.imgtk = imgtk  # Keep a reference to avoid garbage collection

        # Call the function again after a short delay to keep the loop going
        if self.is_measuring:
            video_canvas.after(10, self.measure_loop)

if __name__ == "__main__":
    analyzer = SquatAnalyzer()

    # Create GUI and pass in the callbacks
    root, knee_angle_label, femur_angle_label, video_canvas = create_gui(analyzer.start_measurement, analyzer.stop_measurement)

    # Start the GUI loop
    root.mainloop()
