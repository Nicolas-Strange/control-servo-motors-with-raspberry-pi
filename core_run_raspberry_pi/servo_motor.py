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
        min_duty = conf.get("min_duty_ms", 0.5)  # maximum angle of the servo
        max_duty = conf.get("max_duty_ms", 2.5)  # maximum angle of the servo

        self._min_speed = conf.get("min_speed_d_s", 7)  # min speed of the servo
        self._max_speed = conf.get("max_speed_d_s", 400)  # maximum speed of the servo
        self._speed_config = conf.get("speed_config", {})

        self._percent_min = min_duty / period * 100
        self._percent_max = max_duty / period * 100

        self._min_duty = self._angle_to_duty(self._max_angle / 2)
        self._max_duty = self._angle_to_duty(- 1 * self._max_angle / 2)

        self._min_increment = (self._percent_max - self._percent_min) / self._max_angle

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(signal_pin, GPIO.OUT)
        self._servo = GPIO.PWM(signal_pin, 1 / period * 1000)
        self._current_angle = 0
        self._servo.start((self._percent_max - self._percent_min) / 2 + self._percent_min)

    def go_to_position(self, angle: int, percent_speed: float) -> tuple:
        """
        To set the position of the servo in degrees, we have set up the position with 0 corresponding to the middle,
        positive angles to clockwise rotation, and negative angles to counterclockwise rotation.
        For example, if the servo can rotate 180 degrees, the middle will be 0, the maximum position on the right
        will be 90 degrees, and the maximum position on the left will be -90 degrees.
        :param angle: position in degree
        :param percent_speed: percentage of the maximum rotation speed
        """
        # range the value of angle between -90 and 90
        angle = max(-self._max_angle / 2, angle)
        angle = min(self._max_angle / 2, angle)

        value_start = self._angle_to_duty(angle=self._current_angle)
        value_end = self._angle_to_duty(angle=angle)

        step_calc, waiting_time = self._get_variable_set(percent_speed)

        step_calc = (self._max_duty - self._min_duty) / step_calc
        increment = step_calc if value_end - value_start > 0 else -step_calc

        if abs(increment) >= abs(angle - self._current_angle):
            self._servo.ChangeDutyCycle(value_end)
            self._current_angle = angle
            return waiting_time, step_calc

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

        self._current_angle = angle
        return waiting_time, step_calc

    def release(self) -> None:
        """ release the PWM """
        self._servo.stop()
        GPIO.cleanup()

    def _angle_to_duty(self, angle: int) -> float:
        """ convert the angle to duty cycle """
        percent_duty = (angle + self._max_angle / 2) / self._max_angle
        return (percent_duty * (self._percent_max - self._percent_min)) + self._percent_min

    def _get_variable_set(self, percent_speed: float) -> tuple:
        """ calculate the best parameter set to rotate the servo at the desired speed """
        percent_speed = min(100., percent_speed)
        percent_speed = max(0., percent_speed)

        speed = self._min_speed + percent_speed * (self._max_speed - self._min_speed) / 100

        for step, value in self._speed_config.items():
            max_speed = value["max_speed"]
            min_speed = value["min_speed"]
            if min_speed <= speed <= max_speed:
                params = value["params"]

                waiting_time = (params[0] / (speed - params[1])) / 1000

                return int(step), waiting_time
