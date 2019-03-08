class Ai:
    def __init__(self, angle=0.0, velocity=0.0, enable=True):
        self.__enabled = enable
        self.__data = {}
        self.__initial_angle = angle
        self.__initial_velocity = velocity
        self.__angle = angle
        self.__velocity = velocity

    def reset(self):
        self.__angle = self.__initial_angle
        self.__velocity = self.__initial_velocity

    def input(self, sensor_data):
        if not sensor_data:
            ValueError("No sensor data")
        self.__data = sensor_data

    def output(self):
        return self.__angle, self.__velocity

    def process(self):
        pass

    @property
    def enabled(self):
        return self.__enabled

    @enabled.setter
    def enabled(self, boolean):
        self.__enabled = boolean

