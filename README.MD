# SPOT MOTORS
This directory includes all required files for the Coding Challenge set by WE.
The spot_motors.py file contains the SpotMotors class. 
The spot_motors_simple.py file contains a simplified version of the class.

# REQUIREMENTS
The dependencies are listed in the requirements.txt.
To install in a virtual environment the following command can be used:
```
virtualenv .env && source .env/bin/activate && pip install -r requirements.txt
```
Alternatively to just install the required dependencies:
```
python3 -m pip install -r requirements.txt
```
A Dockerfile is also included to create your own docker image.
Docker image can be built by:
```
docker build -t username/imagename .
```

# USAGE
The class allows you to set up a connection to a Spot robot. 
Class allows you to power Spot's motors on or off.
Class comes with an estop as well as commands to make spot stand and sit.

To run the test example:
```
python3 spot_motors.py ROBOT_IP
```
