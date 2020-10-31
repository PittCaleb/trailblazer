from math import sqrt, cos, sin, radians
from time import perf_counter
from datetime import datetime
from pprint import pprint
import locale

from pygame import *
from models import *
import tkinter as tk

locale.setlocale(locale.LC_ALL, '')  # Use '' for auto, or force e.g. to 'en_US.UTF-8'


class Path:
    def __init__(self, circle_color, radius, default):
        self.old_position = default.start_position
        self.position = default.start_position
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
        """ Calculate the statistics displayed on the console """
        time_now = perf_counter()
        elapsed_time = time_now - self.start_time
        last_segment_length = time_now - self.last_best_time
        last_seg_time = last_segment_length / float(60)
        gen_min = int((generation - self.last_best_gen) / last_seg_time)

        return time_now, elapsed_time, last_seg_time, gen_min

    def check_collision(self, default):
        """
        Determine if the path has met its demise
         - Going off the edge of the screen
         - Colliding with an obstacle
        :return: True if dead; False otherwise
        """
        # Edge of Screen
        if self.position[0] < 0 or self.position[0] > default.screen_width or \
                self.position[1] < 0 or self.position[1] > default.screen_height:
            return True

        if default.obstacle_objects:
            for obstacle in default.obstacle_objects:
                if obstacle.collidepoint(self.position):
                    return True

        return False

    def distance(self, position):
        """ Simple Pythagorean theorem calculation """
        return sqrt((position[0] - self.position[0]) ** 2 + (position[1] - self.position[1]) ** 2)

    def calculate_score(self, default):
        """
        Score calculation algorythm, the determinator of if one path is better than another
        Today: simple distance between the current position and the goal position
        Future: Integrate the length of the path into formula such that a closer but longer path is not necc better
        """
        dist = self.distance(default.goal)

        return int(dist)

    def move(self, direction, default, draw_only=False):
        """
        Move path from by direction degrees
        :param draw_only: if only drawing, do not update history
        """
        self.old_position = self.position

        diff_x = default.step_distance * cos(radians(direction - 90))
        diff_y = default.step_distance * sin(radians(direction - 90))

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
        """ Coverts a float position tuple into an integer position tuple """
        if old:
            return (int(self.old_position[0]), int(self.old_position[1]))

        return (int(self.position[0]), int(self.position[1]))

    def plot(self, default, circle_color=None, overwrite=True):
        """ Plots a single point on the canvas """
        if overwrite:
            draw.circle(default.screen, Color().VERBOSE, self.display_position(old=True), self.radius)

        if circle_color is not None:
            draw.circle(default.screen, circle_color, self.display_position(), self.radius)
        elif self.dead:
            draw.circle(default.screen, Color().RED, self.display_position(), self.radius)
        elif self.win:
            draw.circle(default.screen, Color().WIN, self.display_position(), self.radius)
        else:
            draw.circle(default.screen, self.color, self.display_position(), self.radius)

        display.update()

    def draw(self, default, parent=False, mod=0):
        """ Draws the entire path on the canvas """
        draw_path = Path(Color().BLUE, default.circle_size, default)

        if parent:
            draw_path.history = self.parent
        else:
            draw_path.history = self.history

        for move in draw_path.history:
            draw_path.move(move, default, True)
            draw_path.plot(default, Color(mod).TERSE, False)

    def update_path_box(self, default):
        """ Update the UI to show the current path """
        default.path_box.delete('1.0', tk.END)
        comma = ', '
        comma = '[{}]'.format(comma.join(map(str, self.parent)))
        default.path_box.insert('1.0', comma)
        default.path_box.update_idletasks()

    def update_generation_field(self, generation, default):
        """ Update the UI to show the current generation """
        default.output_fields['Generation'].delete(0, tk.END)
        default.output_fields['Generation'].insert(0, '{:n}'.format(generation))
        default.output_fields['Generation'].update_idletasks()

    def update_best_score(self, generation, steps, score, default):
        """ Update the UI to show the current best score data """
        default.output_fields['Best Gen'].delete(0, tk.END)
        default.output_fields['Best Gen'].insert(0, '{:n}'.format(generation))
        default.output_fields['Best Gen'].update_idletasks()

        default.output_fields['Best Steps'].delete(0, tk.END)
        default.output_fields['Best Steps'].insert(0, '{:n}'.format(steps))
        default.output_fields['Best Steps'].update_idletasks()

        default.output_fields['Best Score'].delete(0, tk.END)
        default.output_fields['Best Score'].insert(0, '{:n}'.format(score))
        default.output_fields['Best Score'].update_idletasks()

        self.update_path_box(default)

    def advance_generation(self, generation, wins, bests, default):
        """ Advance to the next generation in the simulation following a path termination or victory """
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

            self.update_best_score(generation - 1, self.best_step, self.best_score, default)

            if not bests % 5:
                default.reset_screen()
            self.draw(default, mod=bests)

            self.prev_best = self.best_score
            self.prev_step = self.best_step
            self.parent = self.history.copy()[:best]
            self.prev_win = self.win
            self.best_gen = generation - 1
            self.last_best_time = time_now
            self.last_best_gen = generation - 1

        self.old_position = default.start_position
        self.position = default.start_position
        self.steps = 0
        self.dead = False
        self.score = None
        self.history = []
        self.win = False
        self.best_score = 999
        self.best_step = 999

        return generation, bests
