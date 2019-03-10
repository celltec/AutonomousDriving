import os
import math
import random
from collections import deque
import pygame
from pygame.locals import *
import pymunk
from Ai import Ai


class Car(pygame.sprite.Sprite):
    def __init__(self, track, color=None, pos=None, angle=None, enable_ai=True):
        super().__init__()
        cars = {0: "white", 1: "yellow", 2: "red", 3: "green", 4: "blue"}
        if type(color) == int and color in cars.keys():
            color = cars[color]
        elif color is None or color not in cars.values():
            color = cars[random.randint(0, 4)]
        if pos is None:
            pos = track.starting_pos
        if angle is None:
            angle = track.starting_angle
        self.__track = track
        self.__base_image = pygame.image.load(os.path.join("pictures", "car_" + color + ".png")).convert_alpha()
        self.__image = self.__base_image.copy()
        rect = self.__image.get_rect(center=pos)
        self.__body = pymunk.Body(1, pymunk.moment_for_box(1, (rect.w - 14, rect.h - 16)))
        self.__body.position = pos
        self.__body.angle = math.radians(angle)
        self.__shape = pymunk.Poly.create_box(self.__body, (rect.w - 14, rect.h - 16), 5)
        self.__shape.friction = 1
        self.__shape.sensor = True
        self.__shape.filter = pymunk.ShapeFilter()
        track.space.add(self.__body, self.__shape)
        self.__filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS)
        self.__scan_density = 120
        self.__scan_range = math.sqrt(self.__track.screen.get_width() ** 2 + self.__track.screen.get_height() ** 2)
        self.__scan_angles = [round(x / self.__scan_density * 360) for x in range(self.__scan_density)]
        self.__scan_area = [(math.cos(2 * math.pi / self.__scan_density * x) * self.__scan_range,
                             math.sin(2 * math.pi / self.__scan_density * x) * self.__scan_range)
                            for x in range(0, self.__scan_density + 1)][:-1]
        self.__scan_area.reverse()
        self.__scan_intersections = deque()
        self.__sensor_data = {}
        self._update_sensors()
        self.__ai = Ai(math.degrees(self.angle), self.velocity, enable_ai)

    def __del__(self):
        self.__track.space.remove(self.__body, self.__shape)

    def _update_sensors(self):
        self.__sensor_data = {}
        self.__scan_intersections.clear()
        for scan_point in self.__scan_area:
            segment_info = self.__track.space.segment_query_first(self.pos,
                                                                  tuple(map(sum, zip(self.pos, scan_point))),
                                                                  1, self.__filter)
            if segment_info:
                self.__scan_intersections.append(segment_info.point)
            else:
                self.reset()
                return
        self.__scan_intersections.rotate(1 + round(min(self.__scan_angles, key=lambda x:
                                         abs(x - (math.degrees(self.angle) % 360))) / (360 / self.__scan_density)))
        for angle, intersection in zip(self.__scan_angles, self.__scan_intersections):
            self.__sensor_data[angle] = intersection.get_distance(self.pos)

    def update(self):
        self.enable_collision(self.__track.collision)
        self.__image = pygame.transform.rotate(self.__base_image, -math.degrees(self.angle))
        self._update_sensors()
        if pygame.key.get_pressed()[K_d]:
            if self.__sensor_data:
                self.__track.window.message("{:.0f}".format(self.__sensor_data[0]), (1000, 200), "red")
                self.__track.window.message("{:.0f}".format(self.__sensor_data[48]), (1100, 200), "green")
                self.__track.window.message("{:.0f}".format(self.__sensor_data[312]), (1200, 200), "orange")
                for i, intersection in enumerate(self.__scan_intersections):
                    if i == 0:
                        pygame.draw.line(self.__track.screen, Color("red"), self.pos, intersection, 5)
                        continue
                    if i == 48 / (360 / self.__scan_density):
                        pygame.draw.line(self.__track.screen, Color("green"), self.pos, intersection, 5)
                        continue
                    if i == 312 / (360 / self.__scan_density):
                        pygame.draw.line(self.__track.screen, Color("orange"), self.pos, intersection, 5)
                        continue
                    pygame.draw.line(self.__track.screen, Color("black"), self.pos, intersection, 1)
        self.__track.screen.blit(self.__image, self.__image.get_rect(center=self.pos))

    def drive(self):
        if self.__ai.enabled and self.__sensor_data:
            self.__ai.input(self.__sensor_data)
            self.__ai.process()
            steer, accelerate = self.__ai.output()
            self.__body.apply_force_at_local_point((0, steer), (0, 0))
            self.__body.angular_velocity = steer / 250
            self.__body.apply_force_at_local_point((accelerate, 0), (0, 0))

    def turn_left(self):
        self.__body.apply_force_at_local_point((0, -500), (0, 0))
        self.__body.angular_velocity = -2

    def turn_right(self):
        self.__body.apply_force_at_local_point((0, 500), (0, 0))
        self.__body.angular_velocity = 2

    def accelerate(self):
        self.__body.apply_force_at_local_point((2000, 0), (0, 0))

    def reverse(self):
        self.__body.apply_force_at_local_point((-2000, 0), (0, 0))

    def reset(self):
        self.__body.position = self.__track.starting_pos
        self.__body.angle = math.radians(self.__track.starting_angle)
        self.__body.velocity = (0.0, 0.0)
        self.__ai.reset()

    def enable_collision(self, enable):
        if enable == self.__shape.sensor:
            if enable:
                self.__shape.sensor = False
                self.__filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0x1)
                self.__shape.filter = pymunk.ShapeFilter(categories=0x1)
            else:
                self.__shape.sensor = True
                self.__filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS)
                self.__shape.filter = pymunk.ShapeFilter()

    def toggle_ai(self):
        self.__ai.enabled = not self.__ai.enabled

    @property
    def ai_enabled(self):
        return self.__ai.enabled

    @property
    def pos(self):
        return self.__body.position

    @property
    def angle(self):
        return self.__body.angle

    @property
    def velocity(self):
        return self.__body.velocity
