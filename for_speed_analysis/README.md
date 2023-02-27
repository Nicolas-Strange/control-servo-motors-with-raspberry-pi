# Speed analysis
In this folder, you can find the code that was used to perform the speed analysis of the servo.
The goal was to calculate the linear relationship between the percentage of the maximum speed, 
the number of steps, and the actual speed of the servo.

This study helped me design the final version of the `go_to_position method`, 
which you can find in the `servo_motor.py` file located in the root directory.
The final version of the method only requires the percentage of maximum speed as 
input and automatically calculates the parameter set (number of steps and waiting time 
between each step) to make the servo move at the desired speed.

You can find the full tutorial with all
the explanations. [Here]().


