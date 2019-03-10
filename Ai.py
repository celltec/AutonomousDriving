import random


class Ai:
    def __init__(self, angle=0.0, velocity=0.0, enable=True):
        self.__enabled = enable
        self.__data = {}
        self.__initial_angle = angle
        self.__initial_velocity = velocity
        self.__angle = angle
        self.__velocity = velocity
        self.__random_factor = random.uniform(1, 5)

    def reset(self):
        self.__angle = self.__initial_angle
        self.__velocity = self.__initial_velocity
        self.__random_factor = random.uniform(1, 5)

    def input(self, sensor_data):
        if not sensor_data:
            ValueError("No sensor data")
        self.__data = sensor_data

    def output(self):
        return self.__angle, self.__velocity

    def process(self):
        if self.__data[48] < 80:
            self.__angle = 300 * self.__random_factor
        elif self.__data[312] < 80:
            self.__angle = -300 * self.__random_factor
        else:
            self.__angle = 0

        if self.__data[0] > 100:
            self.__velocity = 1000 * self.__random_factor
        else:
            self.__velocity = 500

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, boolean):
        self.__enabled = boolean

