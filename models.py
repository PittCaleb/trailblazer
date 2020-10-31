from pygame import *


class Default:
    def __init__(self, start_position, goal, verbose, generations,
                 max_moves, win_threshold, mutation_rate, obstacles, splits, width, height, direction_degrees,
                 mutation_freedom, step_distance, circle_size, output_fields=None, screen=None, path_box=None):
        self.start_position = start_position
        self.goal = goal
        self.verbose = verbose
        self.generations = generations
        self.max_moves = max_moves
        self.win_threshold = win_threshold
        self.mutation_rate = mutation_rate
        self.obstacles = obstacles
        self.splits = splits
        self.screen_width = width
        self.screen_height = height
        self.screen = screen
        self.direction_degrees = direction_degrees
        self.mutation_freedom = mutation_freedom
        self.step_distance = step_distance
        self.circle_size = circle_size
        self.output_fields = output_fields
        self.obstacle_objects = []
        self.path_box = path_box

    def reset_screen(self):
        self.obstacle_objects = []
        self.screen.fill(Color().WHITE)

        if self.obstacles:
            for obstacle in self.obstacles['obstacles']:
                if obstacle['type'] == 'Box':
                    left, top, width, height = obstacle['params']
                    inner = (left + 2, top + 2, width - 4, height - 4)
                    obstacle_object = draw.rect(self.screen, Color().PINK, obstacle['params'])
                    draw.rect(self.screen, Color().WHITE, inner)
                elif obstacle['type'] == 'Circle':
                    x, y, radius = obstacle['params']
                    obstacle_object = draw.circle(self.screen, Color().PINK, (x, y), radius)
                    draw.circle(self.screen, Color().WHITE, (x, y), radius - 2)
                self.obstacle_objects.append(obstacle_object)

        draw.line(self.screen, Color().YELLOW, self.start_position, self.goal, 1)


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
