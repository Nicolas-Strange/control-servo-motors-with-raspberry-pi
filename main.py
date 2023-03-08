import json
from time import sleep, time_ns

from servo_motor import ServoController


class Main:
    """ main class that will handle the loop """
    SERVO_NAME = "servo_1"

    def __init__(self):
        """
        init function
        """
        self._servo = ServoController(signal_pin=2, **self._conf[self.SERVO_NAME])

    def run(self) -> None:
        """
        core function to iterate
        For each iteration the motion value will be read
        """

        try:
            min_val_inc = -90
            max_val_inc = 90

            self._servo.go_to_position(angle=min_val_inc, speed=100, increment_factor=250)
            for i in range(1, 5, 1):
                sleep(1)
                print(i)
            self._servo.go_to_position(angle=max_val_inc, speed=100, increment_factor=250)

        except KeyboardInterrupt:
            self._servo.release()

        self._servo.release()


if __name__ == '__main__':
    run = Main()
    run.run()
