import cv2
import cv2.aruco as aruco

def get_aruco_markers(frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Load ArUco dictionary and parameters
    aruco_dict = aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters()

    # Detect markers
    corners, ids, _ = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    return corners, ids

def draw_aruco_markers(frame, corners, ids):
    if corners is not None and len(corners) > 0:
        aruco.drawDetectedMarkers(frame, corners, ids)
    return frame
