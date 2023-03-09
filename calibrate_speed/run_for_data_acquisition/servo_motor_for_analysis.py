from time import sleep
import RPi.GPIO as GPIO


class ServoController:
    """ core class to control a servo motor with any Raspberry Pi except the Pico"""

    def __init__(self, signal_pin: int, **conf):
        """
        init function
        :param signal_pin: GPIO number where the signal of the servo is plugged (yellow wire)
        :param freq: frequency of the PWM (Pulse Width Modulation) in Hz (50 by default)
        """
        period = conf.get("period_ms", 20)  # period of a duty cycle
        self._max_angle = conf.get("max_angle", 180)  # maximum angle of the servo
        min_duty = conf.get("min_duty_ms", 1)  # maximum angle of the servo
        max_duty = conf.get("max_duty_ms", 2)  # maximum angle of the servo
        self._min_sleep = conf.get("min_sleep_s", 0.001)  # minimum sleeping time between each iteration
        self._max_sleep = conf.get("max_sleep_s", 0.1)  # maximum sleeping time between each iteration

        self._percent_min = min_duty / period * 100
        self._percent_max = max_duty / period * 100

        self._min_increment = (self._percent_max - self._percent_min) / self._max_angle

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(signal_pin, GPIO.OUT)
        self._servo = GPIO.PWM(signal_pin, 1 / period * 1000)
        self._current_angle = 0
        self._servo.start((self._percent_max - self._percent_min) / 2 + self._percent_min)

    def go_to_position(self, angle: int, percent_waiting: int, steps: int) -> float:
        """
        To set the position of the servo in degrees, we have set up the position with 0 corresponding to the middle,
        positive angles to clockwise rotation, and negative angles to counterclockwise rotation.
        For example, if the servo can rotate 180 degrees, the middle will be 0, the maximum position on the right
        will be 90 degrees, and the maximum position on the left will be -90 degrees.
        :param angle: position in degree
        :param percent_waiting: value between 1 and 100 corresponding to the percent of the
            maximum waiting time between each step
        :param steps: how many times the minimum increment
        """
        # range the value of angle between -90 and 90
        angle = max(-self._max_angle / 2, angle)
        angle = min(self._max_angle / 2, angle)

        value_start = self._angle_to_duty(angle=self._current_angle)
        value_end = self._angle_to_duty(angle=angle)

        increment = steps * self._min_increment \
            if value_end - value_start > 0 else -self._min_increment * steps

        waiting_time = self._max_sleep - (self._max_sleep - self._min_sleep) * percent_waiting / 100 + self._min_sleep

        self._current_angle = angle
        value_duty = value_start

        in_loop = True
        while in_loop:
            self._servo.ChangeDutyCycle(value_duty)
            value_duty += increment
            if increment > 0:
                in_loop = value_duty <= value_end
            else:
                in_loop = value_duty >= value_end

            if not in_loop:
                self._servo.ChangeDutyCycle(value_end)
            sleep(waiting_time)

        return waiting_time

    def _angle_to_duty(self, angle: int) -> float:
        """ convert the angle to duty cycle """
        percent_duty = (angle + self._max_angle / 2) / self._max_angle
        return (percent_duty * (self._percent_max - self._percent_min)) + self._percent_min

    def release(self) -> None:
        """ release the PWM """
        self._servo.stop()
        GPIO.cleanup()
