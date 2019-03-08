import os
import math
import random
from collections import deque
import pygame
from pygame.locals import *
from pymunk import ShapeFilter
from Ai import Ai


class Car(pygame.sprite.Sprite):
    def __init__(self, track, color=None, ai=True):
        super().__init__()
        cars = {0: "white", 1: "yellow", 2: "red", 3: "green", 4: "blue"}
        if type(color) == int and 0 <= color <= len(cars):
            color = cars[color]
        elif not color:
            color = cars[random.randint(0, 4)]
        self.pos = track.starting_pos
        self.angle = track.starting_angle
        self.velocity = 0.0
        self.__track = track
        self.__acceleration = 0.1
        self.__screen = track.screen
        self.__base_surface = pygame.image.load(os.path.join("pictures", "car_" + color + ".png")).convert_alpha()
        self.__surface = self.__base_surface.copy()
        self.__rect = self.__surface.get_rect(center=self.pos)
        self.__scan_density = 60
        self.__scan_range = math.sqrt(self.__screen.get_width() ** 2 + self.__screen.get_height() ** 2)
        self.__scan_angles = [round(x / self.__scan_density * 360) for x in range(self.__scan_density)]
        self.__scan_area = [(math.cos(2 * math.pi / self.__scan_density * x) * self.__scan_range,
                             math.sin(2 * math.pi / self.__scan_density * x) * self.__scan_range)
                            for x in range(0, self.__scan_density + 1)][:-1]
        self.__scan_area.reverse()
        self.__scan_intersections = deque()
        self.__sensor_data = {}
        self._update_sensors()
        self.__ai = Ai(self.angle, self.velocity, ai)

    def _rotate(self):
        self.__surface = pygame.transform.rotate(self.__base_surface, self.angle)
        self.__rect = self.__surface.get_rect(center=self.__rect.center)

    def _move(self):
        self.__x += math.cos(math.radians(self.angle)) * self.velocity
        self.__y += (-1) * math.sin(math.radians(self.angle)) * self.velocity
        self.__rect.center = (self.__x, self.__y)

    def _update_sensors(self):
        self.__sensor_data = {}
        self.__scan_intersections.clear()
        for scan_point in self.__scan_area:
            segment_info = self.__track.space.segment_query_first(self.__rect.center,
                                                                  tuple(map(sum, zip(self.__rect.center, scan_point))),
                                                                  1, ShapeFilter(mask=0xffffffff))
            if segment_info:
                self.__scan_intersections.append(segment_info.point)
            else:
                self.reset()
                return
        self.__scan_intersections.rotate(
            round((-1) * min(self.__scan_angles, key=lambda x: abs(x - self.angle)) / (360 / self.__scan_density)))
        for angle, intersection in zip(self.__scan_angles, self.__scan_intersections):
            self.__sensor_data[angle] = intersection.get_distance(self.__rect.center)

    def update(self):
        self._rotate()
        self._move()
        self._update_sensors()
        if pygame.key.get_pressed()[K_d]:
            if len(self.__sensor_data) != 0:
                for intersection in self.__scan_intersections:
                    pygame.draw.line(self.__screen, Color("red"), self.__rect.center, intersection, 4)
        self.__screen.blit(self.__surface, self.__rect)

    def drive(self):
        if self.__ai.enabled and self.__sensor_data:
            self.__ai.input(self.__sensor_data)
            self.__ai.process()
            self.__angle, self.__velocity = self.__ai.output()

    def reset(self):
        self.pos = self.__track.starting_pos
        self.angle = self.__track.starting_angle
        self.velocity = 0.0
        self.__ai.reset()

    def turn_left(self):
        if self.velocity != 0:
            if self.velocity > 0:
                self.angle += math.pow(self.velocity, 1 / 3)
            elif self.velocity < 0:
                self.angle -= math.pow(math.fabs(self.velocity), 1 / 3)

    def turn_right(self):
        if self.velocity != 0:
            if self.velocity > 0:
                self.angle -= math.pow(self.velocity, 1 / 3)
            elif self.velocity < 0:
                self.angle += math.pow(math.fabs(self.velocity), 1 / 3)

    def accelerate(self):
        self.velocity += self.__acceleration

    def reverse(self):
        self.velocity -= self.__acceleration

    def stop(self):
        if self.velocity > math.pow(self.__acceleration, 1 / 3):
            self.velocity -= math.pow(self.__acceleration, 1 / 3)
        elif self.velocity < (-1) * math.pow(self.__acceleration, 1 / 3):
            self.velocity += math.pow(self.__acceleration, 1 / 3)
        else:
            self.velocity = 0

    def toggle_ai(self):
        self.__ai.enabled = not self.__ai.enabled

    @property
    def ai_enabled(self):
        return self.__ai.enabled

    @property
    def pos(self):
        return self.__x, self.__y

    @pos.setter
    def pos(self, value):
        if type(value) == tuple and len(value) == 2:
            self.__x = float(value[0])
            self.__y = float(value[1])
        else:
            raise ValueError("pos must be tuple(x, y)")

    @property
    def angle(self):
        return self.__angle

    @angle.setter
    def angle(self, value):
        self.__angle = float(value % 360)

    @property
    def velocity(self):
        return self.__velocity

    @velocity.setter
    def velocity(self, value):
        self.__velocity = float(value)
