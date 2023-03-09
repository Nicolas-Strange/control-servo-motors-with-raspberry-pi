import json
from time import sleep, time_ns

from servo_motor import ServoController


class Main:
    """ main class that will handle the loop """
    FILE_NAME = "data_rotation_results"
    SERVO_NAME = "servo_1"

    def __init__(self):
        """
        init function
        """
        # load the servo conf
        with open("params/servo_params.json") as infile:
            self._conf = json.load(infile)

        with open(f'{self.FILE_NAME}.csv', 'w') as fd:
            fd.write('percent_speed,rotation_speed(°/s)\n')

        self._servo = ServoController(signal_pin=2, **self._conf[self.SERVO_NAME])

    def run(self) -> None:
        """
        core function to iterate
        For each iteration the motion value will be read
        """
        try:

            self._servo.go_to_position(angle=-90, percent_speed=100)
            sleep(1)
            for percent_speed in range(0, 110, 10):
                start_time = time_ns()
                waiting_time, step = self._servo.go_to_position(angle=90, percent_speed=percent_speed)

                rotation_time = (time_ns() - start_time) / (10 ** 9)

                print(f"percent_speed: {percent_speed} --- Rotation speed (°/s): {180 / rotation_time} "
                      f"-- waiting_time: {waiting_time} -- step: {step}")

                self._append_file(f"{percent_speed},{180 / rotation_time}")
                sleep(1)
                self._servo.go_to_position(angle=-90, percent_speed=100)
                sleep(1)

        except KeyboardInterrupt:
            self._servo.release()

        self._servo.release()

    def _append_file(self, value: str) -> None:
        """ write in a file: append mode """
        with open(f'{self.FILE_NAME}.csv', 'a') as fd:
            fd.write(f'{value}\n')


if __name__ == '__main__':
    run = Main()
    run.run()
