from math import sqrt, cos, sin, radians
from time import perf_counter
from datetime import datetime
from pprint import pprint
import locale

from pygame import *
from models import *
import tkinter as tk

locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'

class Circle:
    def __init__(self, circle_color, radius, default):
        self.old_position = (default.startx, default.starty)
        self.position = (default.startx, default.starty)
        self.color = circle_color
        self.steps = 0
        self.radius = radius
        self.dead = False
        self.score = 999
        self.best_score = 999
        self.best_step = 999
        self.history = []
        self.parent = []
        self.prev_best = 999
        self.prev_score = 999
        self.prev_step = 999999
        self.win = False
        self.prev_win = False
        self.best_gen = 0
        self.last_best_time = 0
        self.last_best_gen = 0
        self.start_time = perf_counter()

    def stats(self, generation):
        time_now = perf_counter()
        elapsed_time = time_now - self.start_time
        last_segment_length = time_now - self.last_best_time
        last_seg_time = last_segment_length / float(60)
        gen_min = int((generation - self.last_best_gen) / last_seg_time)

        return time_now, elapsed_time, last_seg_time, gen_min

    def check_collision(self, default):
        # Edge of Screen
        if self.position[0] < 0 or self.position[0] > default.screen_width or \
                self.position[1] < 0 or self.position[1] > default.screen_height:
            return True

        # look into RECT.collidepoint(x,y) for easier collission detecting
        # after that works, define OBJECTS are a true JSON object with diff types, i.e. circle, polygon, etc
        if default.boxes:
            for box in default.boxes:
                left, top, width, height = box
                if left <= self.position[0] <= left + width and top <= self.position[1] <= top + height:
                    return True

    def distance(self, position):
        return sqrt((position[0] - self.position[0]) ** 2 + (position[1] - self.position[1]) ** 2)

    def calculate_score(self, default):
        dist = self.distance(default.goal)
        return int(dist)

    def move(self, direction, default, draw_only=False):
        self.old_position = self.position

        diff_x = default.step_distance * cos(radians(direction-90))
        diff_y = default.step_distance * sin(radians(direction-90))

        self.position = (self.position[0] + diff_x, self.position[1] + diff_y)
        self.score = self.calculate_score(default)

        if self.score < self.best_score:
            self.best_score = self.score
            self.best_step = len(self.history)

        if not draw_only:
            self.history.append(direction)

        self.dead = self.check_collision(default)

        if self.score < default.win_threshold:
            self.win = True

    def display_position(self, old=False):
        if old:
            return (int(self.old_position[0]), int(self.old_position[1]))
        return (int(self.position[0]), int(self.position[1]))

    def draw(self, default, circle_color=None, overwrite=True):
        if overwrite:
            draw.circle(default.screen, Color().GREY, self.display_position(old=True), self.radius)

        if circle_color is not None:
            draw.circle(default.screen, circle_color, self.display_position(), self.radius)
        elif self.dead:
            draw.circle(default.screen, Color().RED, self.display_position(), self.radius)
        elif self.win:
            draw.circle(default.screen, Color().GREEN, self.display_position(), self.radius)
        else:
            draw.circle(default.screen, self.color, self.display_position(), self.radius)

        display.update()

    def draw_path(self, default, parent=False):
        path_circle = Circle(Color().BLUE, default.circle_size, default)

        if parent:
            path_circle.history = self.parent
        else:
            path_circle.history = self.history

        for move in path_circle.history:
            path_circle.move(move, default, True)
            path_circle.draw(default, Color().PURPLE, False)

    def update_generation_field(self, generation, default):
        default.output_links['Generation'].delete(0, tk.END)
        default.output_links['Generation'].insert(0, '{:n}'.format(generation))
        default.output_links['Generation'].update_idletasks()

    def update_best_score(self, generation, steps, score, default):
        default.output_links['Best Gen'].delete(0, tk.END)
        default.output_links['Best Gen'].insert(0, '{:n}'.format(generation))
        default.output_links['Best Gen'].update_idletasks()

        default.output_links['Best Steps'].delete(0, tk.END)
        default.output_links['Best Steps'].insert(0, '{:n}'.format(steps))
        default.output_links['Best Steps'].update_idletasks()

        default.output_links['Best Score'].delete(0, tk.END)
        default.output_links['Best Score'].insert(0, '{:n}'.format(score))
        default.output_links['Best Score'].update_idletasks()



    def advance_generation(self, generation, wins, bests, default):
        # pprint(vars(self))

        if not generation % 100:
            self.update_generation_field(generation, default)

        generation += 1
        time_now, elapsed_time, last_seg_time, gen_min = self.stats(generation)

        if default.verbose or self.win or self.best_score < self.prev_best:
            print(
                f'{datetime.now().strftime("%I:%M:%S")}: {elapsed_time / 60:0.1f} mins  Wins: {wins}  Bests: {bests}  Gen {generation - 1:n}  Steps {self.best_step:n}  Score {self.best_score}  Last Seg Time {last_seg_time:0.1f}  Gen/Min = {gen_min:n}')

        best = self.best_step

        if self.win or generation == 1 or self.best_score < self.prev_best:
            bests += 1

            self.update_best_score(generation-1, self.best_step,  self.best_score, default)

            if not bests % 5:
                default.reset_screen()
            self.draw_path(default)

            self.prev_best = self.best_score
            self.prev_step = self.best_step
            self.parent = self.history.copy()[:best]
            self.prev_win = self.win
            self.best_gen = generation - 1
            self.last_best_time = time_now
            self.last_best_gen = generation - 1

        self.old_position = (default.startx, default.starty)
        self.position = (default.startx, default.starty)
        self.steps = 0
        self.dead = False
        self.score = None
        self.history = []
        self.win = False
        self.best_score = 999
        self.best_step = 999

        return generation, bests
