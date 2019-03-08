import sys
if getattr(sys, "frozen", False):
    import os
    from shutil import copy
    copy(os.path.join(sys._MEIPASS, "chipmunk.dll"), os.getcwd())
    os.chdir(sys._MEIPASS)
import pygame
from pygame.locals import *
from Window import Window
from Track import Track
from Car import Car


def main():
    window = Window()
    track = Track(window)
    cars = [Car(track, "yellow", False)]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_r:
                    del cars[1:]
                    cars[0].reset()
                    track.reset()
                if event.key == K_g:
                    cars.append(Car(track))
                if event.key == K_f:
                    cars[0].toggle_ai()
                if event.key == K_t:
                    window.toggle_help()
            if event.type == KEYUP:
                if event.key == K_e:
                    track.generate()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 4:
                    track.cursor_width += 10
                if event.button == 5:
                    track.cursor_width -= 10
        if pygame.key.get_pressed()[K_e]:
            track.edit()
        if not cars[0].ai_enabled:
            if pygame.key.get_pressed()[K_LEFT]:
                cars[0].turn_left()
            if pygame.key.get_pressed()[K_RIGHT]:
                cars[0].turn_right()
            if pygame.key.get_pressed()[K_UP]:
                cars[0].accelerate()
            if pygame.key.get_pressed()[K_DOWN]:
                cars[0].reverse()
            if pygame.key.get_pressed()[K_SPACE]:
                cars[0].stop()

        for car in cars:
            car.drive()

        track.update()
        for car in cars:
            car.update()
        window.update()


if __name__ == "__main__":
    main()
