This is a possible project structure for the squat analysis project:

main.py is the main python program that should be executed when you want to run the GUI and start some measurements



The process of the measurment is focusing on the fundamental parts of the project. 

Requirements for the System (Must Haves):
+ Should be able to measure femur angle with respect to the floor (40 %)
+ Should be able to measure knee angle (10 %)
+ Visualize the two angels in a dashboard (10 %)


To be able to fulfill the given requirements there are several steps necessary. Thinkin of the given requirements we also have to think about the typical process of such a measurement. The scenario is quite simple:

An athlete comes to the sqaut cage for a 1RM test. A soon as the athlete is in position with the handle on his/her shoulders the measurement should start. This can be done by running the code, or we initialize the measurement by clicking a start button in our GUI. Let's go with the minimal approach, as we are only looking at the must haves now, not the extended and optional requirements. If we run the program then, the next step would be a countinuous measurement of the ArUco Codes within the current frame, and pasting the positional information in some sort of datatype. How does this continuous measurement work from a process point of view.

It has to follow a certain loop:

+ Get the current frame from the camera
+ Find the marker (ArUco Codes) within the current frame
+ Calculate the knee and femur angle from the marker (ArUco Codes) position
+ Update the GUI

This is the minimal software structure we would expect. 

The optional requirements are given as:

Integration of a valid squat counter incl. visualization (6 %)
Create a sound every time a valid squat was done & include a check Box for the feature in your visualization (6%)
Integration of a knee angle graph in the visualisation (always visualize the last X seconds) (11%)
Integration of handle tracking incl. visualization of squat hight (6%)
Integration of a handle position graph in the visualisation (always visualize the last Y seconds) (11%)


Each of the given optional requirements would have an impact on the software structure. A possible structure could look like:



Initializing state:
+ Initialize data storage
+ Initialize GUI
+ Initialize timing

Idle state:
+ Waiting for a GUI Callback

GUI Callbacks
+ Start Button (Triggers a state change to Measurement state)
+ Stop Button  (Triggers a state change to Idle state)
+ Sound Checkbox (A change of the checkbox triggers a variable change)
+ Counter Reset Button (Triggers an update of the counter value to 0)

Measurement state
+ Get the current frame from the camera with a time stap
+ Find the marker (ArUco Codes) within the current frame
+ Calculate the current knee and femur angle and the handle position from the marker (ArUco Codes) position
+ Store the time stamp, current knee and femur angle and hnadle position in a respective ditionary/structure
+ Check whether a valid squat has happened and act accordingly (sound + count + squat hight)
+ Update the GUI (both graphs, squat count label, squat hight label)

