from math import sqrt
from time import perf_counter
from datetime import datetime
from pprint import pprint

from pygame import *
from models import *

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

        if direction == 0:  # N
            self.position = (self.position[0], self.position[1] - default.step_distance)
        elif direction == 1:  # NE
            self.position = (self.position[0] + default.step_distance, self.position[1] - default.step_distance)
        elif direction == 2:  # E
            self.position = (self.position[0] + default.step_distance, self.position[1])
        elif direction == 3:  # SE
            self.position = (self.position[0] + default.step_distance, self.position[1] + default.step_distance)
        elif direction == 4:  # S
            self.position = (self.position[0], self.position[1] + default.step_distance)
        elif direction == 5:  # SW
            self.position = (self.position[0] - default.step_distance, self.position[1] + default.step_distance)
        elif direction == 6:  # W
            self.position = (self.position[0] - default.step_distance, self.position[1])
        elif direction == 7:  # NW
            self.position = (self.position[0] - default.step_distance, self.position[1] - default.step_distance)

        self.score = self.calculate_score(default)

        if self.score < self.best_score:
            self.best_score = self.score
            self.best_step = len(self.history)

        if not draw_only:
            self.history.append(direction)

        self.dead = self.check_collision(default)

        if self.score < default.win_threshold:
            self.win = True

    def draw(self, default, circle_color=None, overwrite=True):
        if overwrite:
            draw.circle(default.screen, Color().GREY, self.old_position, self.radius)

        if circle_color is not None:
            draw.circle(default.screen, circle_color, self.position, self.radius)
        elif self.dead:
            draw.circle(default.screen, Color().RED, self.position, self.radius)
        elif self.win:
            draw.circle(default.screen, Color().GREEN, self.position, self.radius)
        else:
            draw.circle(default.screen, self.color, self.position, self.radius)

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

    def advance_generation(self, generation, wins, bests, default):
        # pprint(vars(self))

        generation += 1
        time_now, elapsed_time, last_seg_time, gen_min = self.stats(generation)

        if default.verbose or self.win or self.best_score < self.prev_best:
            print(
                f'{datetime.now().strftime("%I:%M:%S")}: {elapsed_time / 60:0.1f} mins  Wins: {wins}  Bests: {bests}  Gen {generation - 1:n}  Steps {self.best_step:n}  Score {self.best_score}  Last Seg Time {last_seg_time:0.1f}  Gen/Min = {gen_min:n}')

        best = self.best_step

        if self.win or generation == 1 or self.best_score < self.prev_best:
            bests += 1
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