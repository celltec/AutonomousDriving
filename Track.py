import os
import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util
import pymunk.autogeometry
from pymunk import BB


class Track:
    def __init__(self, window, track="default"):
        tracks = {"default": [(1150, 380), 180]}
        self.__starting_pos = tracks[track][0]
        self.__starting_angle = tracks[track][1]
        self.__window = window
        self.__grass = pygame.image.load(os.path.join("pictures", "grass.jpg")).convert()
        self.__base_track = pygame.image.load(os.path.join("pictures", "track_" + str(track) + ".png"))
        self.__track = self.__base_track.copy()
        self.__track_color = (110, 111, 114)
        self.__cursor_width = 80
        self.__cursor_overlay = pygame.Surface((self.__cursor_width * 2, self.__cursor_width * 2), pygame.SRCALPHA)
        self.__cursor_rect = self.__cursor_overlay.get_rect()
        self.__enable_collisions = True
        self.__draw_options = pymunk.pygame_util.DrawOptions(window.screen)
        pymunk.pygame_util.positive_y_is_up = False
        self.generate()

    def edit(self):
        mouse_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            pygame.draw.circle(self.__track, self.__track_color, mouse_pos, self.__cursor_width)
        self.__cursor_rect.center = mouse_pos
        pygame.draw.circle(self.__cursor_overlay, Color("red"), (self.__cursor_width, self.__cursor_width), self.__cursor_width, 4)

    def reset(self):
        self.__track = self.__base_track.copy()
        self.generate()

    def update(self):
        self.__window.screen.blit(self.__grass, (0, 0))
        self.__window.screen.blit(self.__track, (0, 0))
        if pygame.key.get_pressed()[K_e]:
            self.__window.screen.blit(self.__cursor_overlay, self.__cursor_rect)
        if pygame.key.get_pressed()[pygame.K_d]:
            self.__window.space.debug_draw(self.__draw_options)

    def generate(self):
        def segment_func(v0, v1):
            line_set.collect_segment(v0, v1)

        def sample_func(point):
            try:
                p = round(point.x), round(point.y)
                color = self.__track.get_at(p)
                return 255 if color == self.__track_color else 0
            except:
                return 0

        self.__window.instant_message("Generating Track...", (1100, 200), "white")
        for s in self.__window.space.shapes:
            if hasattr(s, "generated") and s.generated:
                self.__window.space.remove(s)
        line_set = pymunk.autogeometry.PolylineSet()
        pymunk.autogeometry.march_soft(
            BB(0, 0, self.__window.width - 1, self.__window.height - 1),
            self.__window.width // 4, self.__window.height // 4, 1, segment_func, sample_func)
        for polyline in line_set:
            line = pymunk.autogeometry.simplify_curves(polyline, 1)
            for i in range(len(line) - 1):
                p1 = line[i]
                p2 = line[i + 1]
                shape = pymunk.Segment(self.__window.space.static_body, p1, p2, 0)
                shape.color = pygame.color.THECOLORS["black"]
                shape.generated = True
                self.__window.space.add(shape)

    def toggle_collisions(self):
        self.__enable_collisions = not self.__enable_collisions

    @property
    def collision(self):
        return self.__enable_collisions

    @property
    def window(self):
        return self.__window

    @property
    def screen(self):
        return self.__window.screen

    @property
    def space(self):
        return self.__window.space

    @property
    def starting_pos(self):
        return self.__starting_pos

    @property
    def starting_angle(self):
        return self.__starting_angle

    @property
    def cursor_width(self):
        return self.__cursor_width

    @cursor_width.setter
    def cursor_width(self, value):
        if value > 0:
            self.__cursor_overlay = pygame.Surface((value * 2, value * 2), pygame.SRCALPHA)
            self.__cursor_rect = self.__cursor_overlay.get_rect()
            self.__cursor_width = value
