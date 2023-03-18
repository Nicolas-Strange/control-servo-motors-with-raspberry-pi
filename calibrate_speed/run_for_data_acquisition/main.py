import json
from time import sleep, time_ns
import RPi.GPIO as GPIO
from servo_motor_for_analysis import ServoController


class Main:
    """ main class that will handle the loop """
    SERVO_NAME = "servo_s53_20"
    FILE_NAME = f"time_analysis_raspberry_3"

    MAX_SPEED = 600

    min_val_inc = -90
    max_val_inc = 90

    def __init__(self):
        """
        init function
        """
        with open("./params/servo_params.json") as infile:
            self._conf = json.load(infile)

        self._servo = ServoController(signal_pin=2, **self._conf[self.SERVO_NAME])

        self._gpio_photo_intercept = 3
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self._gpio_photo_intercept, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _run(self, percent_waiting: int, step: int) -> None:
        """ run one epoch """
        start_time = time_ns()
        waiting_time = \
            self._servo.go_to_position(angle=self.max_val_inc, percent_waiting=percent_waiting, steps=step)

        # While the IR sensor is not activated we wait
        while not GPIO.input(self._gpio_photo_intercept):
            sleep(0.001)

        rotation_time = (time_ns() - start_time) / (10 ** 9)
        rotation_speed = 180 / rotation_time

        self._append_file(f"{rotation_speed},{step},{waiting_time}")

        print(f"rotation_speed(°/s): {rotation_speed} -- "
              f"step: {step} -- waiting_time(s) {waiting_time}")

        self._init_position()

    def run(self) -> None:
        """
        core function to iterate
        For each iteration the motion value will be read
        """

        with open(f'../data/{self.FILE_NAME}_{self.SERVO_NAME}.csv', 'w') as fd:
            fd.write('rotation_speed(°/s),steps,waiting_time(s)\n')

        try:
            self._init_position()
            for step in range(180, 0, -10):
                for percent_waiting in range(100, -1, -1):
                    self._run(percent_waiting=percent_waiting, step=step)

            # full speed
            self._run(percent_waiting=0, step=1)

        except KeyboardInterrupt:
            self._servo.release()

        self._servo.release()

    def _init_position(self):
        """ initialize the servo position """
        sleep(1)
        self._servo.go_to_position(angle=self.min_val_inc, percent_waiting=0, steps=1)
        sleep(1)

    def _append_file(self, value: str) -> None:
        """ write in a file: append mode """
        with open(f'../data/{self.FILE_NAME}_{self.SERVO_NAME}.csv', 'a') as fd:
            fd.write(f'{value}\n')


if __name__ == '__main__':
    run = Main()
    run.run()
