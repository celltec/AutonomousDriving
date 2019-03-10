import os
from ctypes import windll
import pygame
import pymunk


class Window:
    def __init__(self, fullscreen=True):
        pygame.init()
        screen_size = pygame.display.Info()
        self.__width = screen_size.current_w
        self.__height = screen_size.current_h
        windll.user32.SetProcessDPIAware()
        true_res = (windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1))
        if screen_size.current_w < 1920 and screen_size.current_h < 1080:
            raise Exception("Kauf dir mal nen besseren Monitor, alles kleiner als 1080p ist eine Zumutung.")
        elif screen_size.current_w != true_res[0] and screen_size.current_h != true_res[1]:
            self.__width = true_res[0]
            self.__height = true_res[1]
        elif screen_size.current_w > 1920 and screen_size.current_h > 1080:
            self.__width = 1920
            self.__height = 1080
            fullscreen = False
        if not fullscreen:
            self.__screen = pygame.display.set_mode((self.__width, self.__height))
            pygame.display.set_caption("Self driving car")
            pygame.display.set_icon(pygame.image.load(os.path.join("pictures", "icon.png")))
        else:
            self.__screen = pygame.display.set_mode((self.__width, self.__height), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        self.__center = (self.__width // 2, self.__height // 2)
        self.__clock = pygame.time.Clock()
        self.__space = pymunk.Space()
        self.__space.damping = 0.00001
        static = [
            pymunk.Segment(self.__space.static_body, (-1, -1), (-1, self.__height + 1), 0),
            pymunk.Segment(self.__space.static_body, (-1, self.__height + 1), (self.__width + 1, self.__height + 1), 0),
            pymunk.Segment(self.__space.static_body, (self.__width + 1, self.__height + 1), (self.__width + 1, -1), 0),
            pymunk.Segment(self.__space.static_body, (-1, -1), (self.__width + 1, -1), 0)
        ]
        self.__space.add(static)
        self.__font_fps = pygame.font.SysFont("Consolas", 25)
        self.__font_message = pygame.font.SysFont("Calibri", 50)
        self.__messages = []
        help_font = pygame.font.SysFont("Consolas", 25)
        help_text = ["Arrows to move",
                     "E to edit track",
                     "R to reset",
                     "D to show sensors",
                     "F to toggle player AI",
                     "G to spawn new AI car",
                     "C to toggle collisions",
                     "H to toggle help"]
        help_renders = [help_font.render(line, True, pygame.Color("white")) for line in help_text]
        self.__help = [(line, (1600, y)) for line, y in zip(help_renders, range(25, 35 * len(help_text), 35))]
        self.__display_help = True

    def __del__(self):
        pygame.quit()

    def update(self):
        self.__screen.blit(self.__font_fps.render("{:.0f}".format(self.__clock.get_fps()), True, pygame.Color("white")), (15, 15))
        for message in self.__messages:
            self.__screen.blit(message[0], message[1])
            self.__messages.remove(message)
        if self.__display_help:
            self.__screen.blits(self.__help)
        self.__space.step(1/60)
        self.__clock.tick(60)
        pygame.display.flip()

    def message(self, text, pos, color="black", background=None):
        message = self.__font_message.render(text, True, pygame.Color(color), pygame.Color(background) if background is not None else None)
        rect = message.get_rect(center=pos)
        self.__messages.append((message, rect))

    def instant_message(self, text, pos, color="black", background=None):
        self.message(text, pos, color, background)
        message, rect = self.__messages.pop()
        self.__screen.blit(message, rect)
        pygame.display.flip()

    def toggle_help(self):
        self.__display_help = not self.__display_help

    @property
    def screen(self):
        return self.__screen

    @property
    def space(self):
        return self.__space

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def center(self):
        return self.__center

