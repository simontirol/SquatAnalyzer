import tkinter as tk
import cv2
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from squat_analyzer import SquatAnalyzer
import numpy as np
from collections import deque
import pygame
import time

class SquatApp:
    def __init__(self, root):
        self.root = root
        self.squat_analyzer = None  # Initialize as None
        self.squat_counter = 0
        self.is_measuring = False

        # Knee angle and handle position graph history
        self.knee_angle_history = deque(maxlen=100)
        self.handle_position_history = deque(maxlen=100)
        
        # Store the after call ID
        self.update_id = None

        # Set up the GUI layout
        self.setup_gui()

    def setup_gui(self):
        """Initialize the GUI components."""

        # Set the window size to match the screen resolution
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
    
        # Set geometry to fill the screen
        self.root.geometry(f"{screen_width}x{screen_height}")
    
        # Maximize window (keeps title bar and other controls)
        self.root.state('zoomed')  # This works for Windows, on Linux it may have different effects

        # Start and Stop buttons
        self.start_button = tk.Button(self.root, text="Start", command=self.start_measurement)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_measurement)
        self.stop_button.grid(row=1, column=0, padx=5, pady=5)

        # Traffic light label
        self.traffic_light_label = tk.Label(self.root, text="No Squat Detected", width=20, height=2, bg="red")
        self.traffic_light_label.grid(row=0, column=1, padx=5, pady=5)

        # Squat count label
        self.squat_count_label = tk.Label(self.root, text="Squat Count: 0", width=20)
        self.squat_count_label.grid(row=1, column=1, padx=5, pady=5)

        # Checkbox for the sound
        self.sound_checkbox_var = tk.BooleanVar()
        self.sound_checkbox = tk.Checkbutton(self.root, text="Sound when valid squat is made", variable=self.sound_checkbox_var)
        self.sound_checkbox.grid(row=2, column=0, padx=5, pady=5)

        # Femur angle label
        self.femur_angle_label = tk.Label(self.root, text="Femur Angle: N/A", width=20)
        self.femur_angle_label.grid(row=0, column=2, padx=5, pady=5)

        # Knee angle label
        self.knee_angle_label = tk.Label(self.root, text="Knee Angle: N/A", width=20)
        self.knee_angle_label.grid(row=1, column=2, padx=5, pady=5)

        # Placeholder live view with instructions
        self.live_feed_label = tk.Label(self.root, text="Instructions:\n1. Marker 1 --> Hips\n2. Marker 2 --> Knee\n3. Marker 3 --> Ankle\n4. Marker 4 --> Weight\n5. Press 'Start' Button to start the measurement\n6. Ensure all markers are visible in the live view", bg="darkgrey", width=40, height=10)
        self.live_feed_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Knee angle graph (using Matplotlib) on the right side
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(3, 3))  # Two subplots
        self.fig.subplots_adjust(hspace=0.8) # Increase spacing between graphs 
        self.ax1.set_title("Knee Angle Over Time")
        self.ax1.set_xlabel("Time (frames)")
        self.ax1.set_ylabel("Knee Angle / °")
        
        # Handle position graph
        self.ax2.set_title("Handle Position Over Time")
        self.ax2.set_xlabel("Time (frames)")
        self.ax2.set_ylabel("Handle Position / cm")

        self.knee_angle_canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.knee_angle_canvas.get_tk_widget().grid(row=3, column=2, rowspan=1, padx=5, pady=5, sticky="nsew")

        # Configure column and row weights to ensure proper resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=1)


    def start_measurement(self):
        """Start the squat measurement."""
        self.squat_analyzer = SquatAnalyzer()  # Initialize SquatAnalyzer
        self.is_measuring = True
        self.update_live_feed()  # Start the live feed update loop

    def stop_measurement(self):
        """Stop the squat measurement."""
        if self.squat_analyzer:
            self.squat_analyzer.cap.release()  # Release the camera
            self.squat_analyzer = None
            self.squat_counter = 0  # Clean up

        if self.update_id:  # Check if there's an ongoing update
            self.root.after_cancel(self.update_id)  # Cancel the live feed update
            self.update_id = None  # Reset the update_id

        self.is_measuring = False

    def play_beeb_sound(self):
        """Play a beeb sound for a valid squat"""
        pygame.mixer.init(frequency=44100, size=-16, channels=2)

        # Generate a 440 Hz sine wave (A4 note)
        sample_rate = 44100
        duration = 1.0  # seconds
        frequency = 440.0  # Frequency of the beeb sound
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        samples = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

        # Create a stereo sound by duplicating the mono samples
        stereo_samples = np.zeros((len(samples), 2), dtype=np.int16)
        stereo_samples[:, 0] = samples  # Left channel
        stereo_samples[:, 1] = samples  # Right channel

        sound = pygame.sndarray.make_sound(stereo_samples)
        sound.play()
        time.sleep(1)
        pygame.mixer.quit()

    def update_live_feed(self):
        """Update the live video feed with detected markers and update the GUI components."""
        if self.squat_analyzer and self.is_measuring:
            ret, frame = self.squat_analyzer.cap.read()
            if ret:
                # Detect ArUco markers
                corners, ids, _ = self.squat_analyzer.detect_aruco_markers(frame)

                if ids is not None:
                    # Draw markers and lines between them
                    frame = self.squat_analyzer.draw_lines_between_markers(frame, corners, ids)

                    # Calculate angles and handle position
                    femur_angle = self.squat_analyzer.calculate_femur_angle(corners, ids)
                    knee_angle = self.squat_analyzer.calculate_knee_angle(corners, ids)
                    handle_position = self.squat_analyzer.get_handle_position(corners, ids)

                    # Update angle and position labels
                    if femur_angle is not None:
                        self.femur_angle_label.config(text=f"Femur Angle: {femur_angle:.2f}")
                    if knee_angle is not None:
                        self.knee_angle_label.config(text=f"Knee Angle: {knee_angle:.2f}")
                        self.knee_angle_history.append(knee_angle)
                        self.update_knee_angle_graph()

                    if handle_position is not None:
                        self.handle_position_history.append(handle_position)
                        self.update_handle_position_graph()

                    # Squat validation
                    self.update_traffic_light(femur_angle)

                # Convert image to Tkinter format and update live feed label
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.live_feed_label.imgtk = imgtk
                self.live_feed_label.config(image=imgtk)

        # Schedule the next update
        self.update_id = self.root.after(5, self.update_live_feed)

    def update_traffic_light(self, femur_angle):
        """Update the traffic light indicator based on femur angle."""
        if femur_angle is not None:
            if femur_angle < 0:  # Valid squat range
                self.traffic_light_label.config(bg="green", text="Squat Valid")
                if not self.squat_analyzer.squat_valid and self.squat_analyzer.squat_started:  # If a new valid squat
                    self.squat_counter += 1
                    self.squat_analyzer.squat_started = False
                    self.squat_analyzer.squat_valid = True
                    self.squat_count_label.config(text=f"Squat Count: {self.squat_counter}")
                    if self.sound_checkbox_var.get():
                        self.play_beeb_sound()
            elif femur_angle <= 10:  # Close to valid
                self.traffic_light_label.config(bg="yellow", text="Almost There")
                self.squat_analyzer.squat_started = True
                self.squat_analyzer.squat_valid = False
            else:  # Invalid squat
                self.traffic_light_label.config(bg="red", text="Squat Invalid")
                self.squat_analyzer.squat_started = True
                self.squat_analyzer.squat_valid = False
        else:
            self.traffic_light_label.config(bg="red", text="No Squat Detected")
            self.squat_analyzer.squat_started = False
            self.squat_analyzer.squat_valid = False

    def update_knee_angle_graph(self):
        """Update the knee angle graph with the latest data."""
        self.ax1.clear()
        self.ax1.plot(self.knee_angle_history, label="Knee Angle")
        self.ax1.set_title("Knee Angle Over Time")
        self.ax1.set_xlabel("Time / frames")
        self.ax1.set_ylabel("Knee Angle / °")
        self.ax1.legend()
        self.knee_angle_canvas.draw()

    def update_handle_position_graph(self):
        """Update the handle position graph with the latest data."""
        self.ax2.clear()
        self.ax2.plot(self.handle_position_history, label="Handle Position", color="orange")
        self.ax2.set_title("Handle Position Over Time")
        self.ax2.set_xlabel("Time / frames")
        self.ax2.set_ylabel("Handle Position / cm")
        self.ax2.legend()
        self.knee_angle_canvas.draw()
