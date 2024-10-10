import numpy as np
import cv2

def get_knee_angle(corners, ids):
    """Calculate the knee angle based on marker positions."""
    if ids is None:
        return None

    ids_flat = ids.flatten()

    # Check if the required markers (1, 2, 3) are detected
    if 1 in ids_flat and 2 in ids_flat and 3 in ids_flat:
        # Get the index of each marker
        hip_idx = list(ids_flat).index(1)
        knee_idx = list(ids_flat).index(2)
        ankle_idx = list(ids_flat).index(3)

        # Get the corner positions for each marker
        hip = corners[hip_idx][0][0]  # Marker 1 (hip)
        knee = corners[knee_idx][0][0]  # Marker 2 (knee)
        ankle = corners[ankle_idx][0][0]  # Marker 3 (ankle)

        # Calculate vectors
        vec1 = knee - hip  # Vector from hip to knee
        vec2 = ankle - knee  # Vector from knee to ankle

        # Calculate the angle between the two vectors
        angle = calculate_angle(vec1, vec2)

        return angle

    return None

def get_femur_angle(corners, ids):
    """Calculate the femur angle with respect to the floor."""
    if ids is None:
        return None

    ids_flat = ids.flatten()

    # Check if the required markers (1 and 2) are detected (hip and knee)
    if 1 in ids_flat and 2 in ids_flat:
        # Get the index of each marker
        hip_idx = list(ids_flat).index(1)
        knee_idx = list(ids_flat).index(2)

        # Get the corner positions for each marker
        hip = corners[hip_idx][0][0]  # Marker 1 (hip)
        knee = corners[knee_idx][0][0]  # Marker 2 (knee)

        # Calculate the vector from hip to knee
        vec_femur = knee - hip

        # The reference vector is horizontal (parallel to the floor)
        ref_vector = np.array([1, 0])  # Assuming the camera is parallel to the floor

        # Calculate the angle between the femur and the floor
        angle = calculate_angle(vec_femur, ref_vector)

        return angle

    return None

def calculate_angle(vec1, vec2):
    """Calculate the angle between two vectors."""
    unit_vec1 = vec1 / np.linalg.norm(vec1)
    unit_vec2 = vec2 / np.linalg.norm(vec2)
    dot_product = np.dot(unit_vec1, unit_vec2)
    
    # Clamp dot_product to avoid floating point precision issues
    dot_product = np.clip(dot_product, -1.0, 1.0)

    angle = np.arccos(dot_product)  # Result is in radians
    angle_degrees = np.degrees(angle)  # Convert to degrees

    return angle_degrees
