from pygame import *


class Default:
    def __init__(self, startx, starty, goal, verbose, generations,
                 max_moves, win_threshold, mutation_rate, boxes, splits, width, height, direction_degrees,
                 mutation_freedom, step_distance, circle_size, output_links=None, screen=None, ):
        self.startx = startx
        self.starty = starty
        self.goal = goal
        self.verbose = verbose
        self.generations = generations
        self.max_moves = max_moves
        self.win_threshold = win_threshold
        self.mutation_rate = mutation_rate
        self.boxes = boxes
        self.splits = splits
        self.screen_width = width
        self.screen_height = height
        self.screen = screen
        self.direction_degrees = direction_degrees
        self.mutation_freedom = mutation_freedom
        self.step_distance = step_distance
        self.circle_size = circle_size
        self.output_links = output_links

    def reset_screen(self):
        self.screen.fill(Color().WHITE)

        if self.boxes:
            for box in self.boxes:
                left, top, width, height = box
                inner = (left + 2, top + 2, width - 4, height - 4)
                draw.rect(self.screen, Color().PINK, box)
                draw.rect(self.screen, Color().WHITE, inner)

        draw.line(self.screen, Color().YELLOW, (self.startx, self.starty), self.goal, 1)


class Color:
    def __init__(self):
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 128, 255)
        self.GREY = (128, 128, 128)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.PURPLE = (191, 87, 231)
        self.PINK = (255, 20, 147)
        self.YELLOW = (252, 237, 135)
