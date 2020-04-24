# Turtle Bot Food Delivery System
This project was build as a requirement for course CSE 571 Artificial Intelligence at Arizona State University.
This system simulates a TurtleBot in Gazebo environment. It simulates a robot whose objective is to reach all destination nodes in the generated grid. The bot tries to find the most optimal plan.

## Running the project
1) Install TurtleBot3.
2) Clone this repository, extract content in the source folder.
3) Navigate to src folder 
4) Run "python server.py" to run the server.
5) Run the roscore command to enable movement.
6) Run astar.py. This script tries to find a plan for the turtlebot. If it finds plans, it sends navigation commands to the turtlebot using pid controller.
7) If a plan is generated, the turtle will start moving to the requirement location.

## Demo
Please refer to [this](https://youtu.be/Wmlp68KuTkI) demo video

## Future work
* Adding obstacles
* Simulating same problem in different types of environments (non-observable, partially observable, stochastic, non-stochastic)

## Additional Resources
The AAIR lab  at ASU has various projects posted on their github page. Please check them out [here](https://github.com/AAIR-lab/planning)