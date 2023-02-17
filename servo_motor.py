from time import sleep
import RPi.GPIO as GPIO


class ServoController:
    """ core class to control a servo motor with any Raspberry Pi except the Pico"""

    def __init__(self, signal_pin: int, freq: int = 50, **conf):
        """
        init function
        :param signal_pin: GPIO number where the signal of the servo is plugged (yellow wire)
        :param freq: frequency of the PWM (Pulse Width Modulation) in Hz (50 by default)
        """
        self._signal_pin = signal_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(signal_pin, GPIO.OUT)
        self._servo = GPIO.PWM(signal_pin, freq)
        GPIO.output(self._signal_pin, True)

        self._max_angle = conf.get("max_angle", 90)  # maximum operating angle
        self._min_sleep = conf.get("min_sleep", 0.0001)  # minimum sleeping time between each iteration
        self._max_sleep = conf.get("max_sleep", 0.005)  # maximum sleeping time between each iteration

        self._current_angle = 0
        self.go_to_position(angle=0, speed=100, inc=1)

    def go_to_position(self, angle: int, speed: int, inc: int):
        """
        set the position of the servo in degree.
        we have setup the position with 0 corresponding to the middle, positive angles to clock-wise,
        and negative angles to counter clock-wise.
        e.g. if the servo can rotate 180 degrees, the middle will be 0, the max on the right will be 90 and the max
        on the left will be -90.
        :param angle: position in degree
        :param speed: value between 1 and 100 corresponding to the percent of the maximum speed of the servo
        :param inc: incrementation for each epoch
        """
        # range the value of angle between -90 and 90
        angle = max(-self._max_angle/2, angle)
        angle = min(self._max_angle/2, angle)

        value_start = self._angle_to_duty(angle=self._current_angle)
        value_end = self._angle_to_duty(angle=angle)

        increment = inc if value_end - value_start > 0 else -inc
        sleep_iter = self._max_sleep - (self._max_sleep - self._min_sleep) * speed / 100 + self._min_sleep

        self._current_angle = angle
        for value in range(value_start, value_end + increment, increment):
            self._servo.ChangeDutyCycle(value)
            sleep(sleep_iter)

    def release(self) -> None:
        """ release the PWM """
        GPIO.output(self._signal_pin, False)

    def _angle_to_duty(self, angle: int) -> int:
        """ convert the angle to duty cycle """
        return int((angle + self._max_angle / 2) / self._max_angle * 100)
