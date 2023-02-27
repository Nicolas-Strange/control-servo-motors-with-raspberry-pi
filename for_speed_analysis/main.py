import json
from time import sleep, time_ns

from servo_motor_for_analysis import ServoController


class Main:
    """ main class that will handle the loop """
    SERVO_NAME = "servo_1"

    def __init__(self):
        """
        init function
        """
        with open("../params/servo_params.json") as infile:
            self._conf = json.load(infile)

        self._servo = ServoController(signal_pin=2, **self._conf[self.SERVO_NAME])

    def run(self) -> None:
        """
        core function to iterate
        For each iteration the motion value will be read
        """

        min_val_inc = -90
        max_val_inc = 90

        with open('output.csv', 'w') as fd:
            fd.write('speed(%),time(s),increment,sleep_iter(s)\n')

        try:
            self._servo.go_to_position(angle=min_val_inc, speed=100, increment_factor=250)
            for inc in range(1, 230, 1):
                for sleep_tm in range(5, 105, 5):
                    init_time = time_ns()
                    sleep_iter = self._servo.go_to_position(angle=max_val_inc, speed=sleep_tm, increment_factor=inc)
                    time_proc = (time_ns() - init_time) / (10 ** 9)
                    append_file(f"{sleep_tm},{time_proc},{inc},{sleep_iter}")
                    print(f"speed: {sleep_tm}% -- time: {time_proc}s -- increment: {inc} -- sleep_iter {sleep_iter}")
                    sleep(1)
                    self._servo.go_to_position(angle=min_val_inc, speed=100, increment_factor=250)
                    sleep(1)
        except KeyboardInterrupt:
            self._servo.release()

        self._servo.release()


def append_file(value: str) -> None:
    """ write in a file: append mode """
    with open('output.csv', 'a') as fd:
        fd.write(f'{value}\n')


if __name__ == '__main__':
    run = Main()
    run.run()
