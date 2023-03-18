import json
from time import sleep, time_ns

from RPi import GPIO

from servo_motor import ServoController


class Main:
    """ main class that will handle the loop """
    FILE_NAME = "data_rotation_results"
    SERVO_NAME = "servo_sg9"

    min_val_inc = -90
    max_val_inc = 90

    def __init__(self):
        """
        init function
        """
        # load the servo conf
        with open("params/servo_params.json") as infile:
            self._conf = json.load(infile)

        with open(f'../calibrate_speed/data/{self.FILE_NAME}_{self.SERVO_NAME}.csv', 'w') as fd:
            fd.write('percent_speed,rotation_speed(°/s)\n')

        self._servo = ServoController(signal_pin=2, **self._conf[self.SERVO_NAME])

        self._gpio_photo_intercept = 3
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self._gpio_photo_intercept, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _run(self, percent_speed: float) -> None:
        """ run one epoch """
        start_time = time_ns()

        waiting_time, step = self._servo.go_to_position(angle=self.max_val_inc, percent_speed=percent_speed)

        # While the IR sensor is not activated we wait
        while not GPIO.input(self._gpio_photo_intercept):
            sleep(0.001)

        rotation_time = (time_ns() - start_time) / (10 ** 9)
        rotation_speed = 180 / rotation_time

        self._append_file(f"{percent_speed},{rotation_speed}")

        print(f"rotation_speed(°/s): {rotation_speed} -- "
              f"step: {step} -- waiting_time(s) {waiting_time}")

        self._init_position()

    def run(self) -> None:
        """
        core function to iterate
        For each iteration the motion value will be read
        """
        try:
            self._init_position()
            for percent_speed in range(0, 110, 10):
                self._run(percent_speed=percent_speed)

        except KeyboardInterrupt:
            self._servo.release()

        self._servo.release()

    def _init_position(self):
        """ initialize the servo position """
        sleep(1)
        self._servo.go_to_position(angle=self.min_val_inc, percent_speed=100)
        sleep(1)

    def _append_file(self, value: str) -> None:
        """ write in a file: append mode """
        with open(f'../calibrate_speed/data/{self.FILE_NAME}_{self.SERVO_NAME}.csv', 'a') as fd:
            fd.write(f'{value}\n')


if __name__ == '__main__':
    run = Main()
    run.run()
