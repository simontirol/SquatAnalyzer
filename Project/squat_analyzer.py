import cv2
import numpy as np
from collections import deque

class SquatAnalyzer:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)  # Initialize the camera
        self.squat_count = 0
        self.play_sound = False  # Toggle sound feature
        self.femur_angle_threshold = 0  # Threshold for a valid squat
        self.previous_handle_y = None  # Store previous handle Y position for movement tracking

    def detect_aruco_markers(self, frame):
        """Detect ArUco markers."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        parameters = cv2.aruco.DetectorParameters()
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        # Detect the markers
        corners, ids, rejected = detector.detectMarkers(gray)
        return corners, ids, rejected

    def calculate_femur_angle(self, corners, ids):
        """Calculate femur angle based on markers."""
        if ids is None:
            return None
        ids_flat = ids.flatten()
        if 1 in ids_flat and 2 in ids_flat:
            hip_idx = list(ids_flat).index(1)
            knee_idx = list(ids_flat).index(2)
            hip = corners[hip_idx][0][0]
            knee = corners[knee_idx][0][0]
            angle = np.degrees(np.arctan2(knee[1] - hip[1], knee[0] - hip[0]))
            return angle
        return None


    def calculate_knee_angle(self, corners, ids):
        """Calculate the knee angle between femur and shinbone based on markers."""
        if ids is None:
            return None
        
        ids_flat = ids.flatten()
        if 1 in ids_flat and 2 in ids_flat and 3 in ids_flat:
            # Indices for the hip, knee, and ankle markers
            hip_idx = list(ids_flat).index(1)
            knee_idx = list(ids_flat).index(2)
            ankle_idx = list(ids_flat).index(3)
            
            # Extract marker positions
            hip = corners[hip_idx][0][0]
            knee = corners[knee_idx][0][0]
            ankle = corners[ankle_idx][0][0]
            
            # Vectors for femur and shinbone
            femur_vector = knee - hip
            shinbone_vector = ankle - knee
            
            # Calculate the angle between the vectors
            dot_product = np.dot(femur_vector, shinbone_vector)
            norm_femur = np.linalg.norm(femur_vector)
            norm_shinbone = np.linalg.norm(shinbone_vector)
            
            if norm_femur == 0 or norm_shinbone == 0:
                return None  # Avoid division by zero
            
            # Angle in radians
            angle_radians = np.arccos(dot_product / (norm_femur * norm_shinbone))
            
            # Convert to degrees
            angle_degrees = 180 - np.degrees(angle_radians)
            return angle_degrees
        
        return None


    def get_handle_position(self, corners, ids):
        """Get handle height in cm using ArUco marker and track movement."""
        if ids is None:
            return None

        ids_flat = ids.flatten()
        if 4 in ids_flat:
            handle_idx = list(ids_flat).index(4)
            handle_corners = corners[handle_idx][0]  # Corners of marker 4

            # Calculate pixel-to-cm ratio based on marker size (5.7 cm)
            marker_width_pixels = np.linalg.norm(handle_corners[0] - handle_corners[1])
            pixels_per_cm = marker_width_pixels / 5.7

            # Get the current Y position in pixels and convert to cm
            current_y_pixels = handle_corners[0][1]
            current_y_cm = current_y_pixels / pixels_per_cm

            return current_y_cm

        return None

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