import random
import locale

import tkinter as tk

import pygame

from circle import Circle
from models import *

locale.setlocale(locale.LC_ALL, '')

# Defaults
WIDTH = 640
HEIGHT = 480

GOAL = (WIDTH, 0)
VERBOSE = False
GENERATIONS = 1000000
MAX_MOVES = 2500
WIN_THRESHOLD = 25
MUTATION_RATE = 50
SPLITS = 50
MUTATION_FREEDOM = 180

# Examples
# BOXES = ((240, 150, 90, 90), (240, 275, 200, 70), (150, 50, 60, 150), (440, 75, 50, 50))  # left, top, width, height
# BOXES = "(150, 50, 300, 175), (300, 300, 300, 75), (500, 200, 50, 25)"
BOXES = ((280, 200, 80, 80), (0,300,10,10))
# Currently being reset inside SetupDefaults until I can parse this correctly
# copy this line to setupDefaults if you want to use a box

STEP_DISTANCE = 2
CIRCLE_SIZE = 2

input_fields = {'X Start': 0,
                'Y Start': HEIGHT,
                'Goal': str(GOAL),
                'Verbose': "True" if VERBOSE else "False",
                'Generations': GENERATIONS,
                'Max Moves': MAX_MOVES,
                'Win Threshold': WIN_THRESHOLD,
                'Mutation Rate': MUTATION_RATE,
                'Obstacles': BOXES,
                'Splits': SPLITS,
                'Mutation Freedom': MUTATION_FREEDOM}


def makeform(root, fields):
    entries = {}
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=22, text=field + ": ", anchor='w')
        ent = tk.Entry(row)
        ent.insert(0, fields[field])
        row.pack(side=tk.TOP,
                 fill=tk.X,
                 padx=5,
                 pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT,
                 expand=tk.YES,
                 fill=tk.X)
        entries[field] = ent
    return entries


def draw_path(path, default):
    path_circle = Circle(Color().BLUE, CIRCLE_SIZE, default)
    path_circle.history = path
    path_circle.draw_path(default)


def set_values_from_form(entries, output_links):
    for entry in entries:
        entry_key = entry
        value = entries[entry].get()

        if entry_key == 'X Start':
            startx = int(value)

        if entry_key == 'Y Start':
            starty = int(value)

        if entry_key == 'Goal':
            x, y = value.replace('(', '').replace(')', '').split(',')
            goal = (int(x), int(y))

        if entry_key == 'Verbose':
            if value.lower() == 'true':
                verbose = True
            else:
                verbose = False

        if entry_key == 'Generations':
            generations = int(value)

        if entry_key == 'Max Moves':
            max_moves = int(value)

        if entry_key == 'Win Threshold':
            win_threshold = int(value)

        if entry_key == 'Mutation Rate':
            mutation_rate = int(value)

        if entry_key == 'Obstacles':
            print(value)
            boxes = value.split(',')
            print(boxes)
            print('MUST fix handling boxes')
            boxes = BOXES

        if entry_key == 'Splits':
            splits = int(value)

        if entry_key == 'Mutation Freedom':
            mutation_freedom = int(value)

    direction_degrees = 359  # Not user settable, but needs stored in default

    print(
        'Initating Simulation with:\nstartx={}, starty={}, goal={}, verbose={}, generations={}, max_moves={}, win_threshold={}, mutation_rate={}, obstacles={}, splits={}'.format(
            startx, starty, goal, verbose, generations, max_moves, win_threshold, mutation_rate, boxes, splits))

    return Default(startx=startx, starty=starty, goal=goal, verbose=verbose, generations=generations,
                   max_moves=max_moves, win_threshold=win_threshold, mutation_rate=mutation_rate, boxes=boxes,
                   splits=splits, width=WIDTH, height=HEIGHT, direction_degrees=direction_degrees,
                   mutation_freedom=mutation_freedom, step_distance=STEP_DISTANCE, circle_size=CIRCLE_SIZE,
                   output_links=output_links)


def get_move_limit(generation, default, circle):
    if circle.prev_win:
        return circle.prev_step

    generation_step = default.generations / default.splits
    generation_steps = int(generation / generation_step) + 1

    return (default.max_moves / default.splits) * generation_steps


def direction_correct(direction):
    if direction > 7:
        return direction - 8
    elif direction < 0:
        return direction + 8
    return direction


def get_direction(generation, circle, default):
    if generation > 0 and circle.steps < len(circle.parent):
        mutate = random.randint(0, 100) < default.mutation_rate

        if mutate:
            mutation_plus_minus = int(default.mutation_freedom / 2)
            mutation_direction = random.randint(-1 * mutation_plus_minus, mutation_plus_minus)
            return direction_correct(circle.parent[circle.steps] + mutation_direction)
        else:
            return circle.parent[circle.steps]

    return random.randint(0, default.direction_degrees)


def initialize_pygame(default):
    pygame.init()
    default.screen = display.set_mode((WIDTH, HEIGHT), 0, 32)
    display.set_caption("Trailblazer")
    default.reset_screen()
    return default


def run_simulation(entries, output_links):
    default = set_values_from_form(entries, output_links)
    default = initialize_pygame(default)
    doit(default)


def doit(default):
    generation = 0
    win_count = 0
    best_count = 0

    circle = Circle(Color().BLUE, CIRCLE_SIZE, default)

    while generation < default.generations:
        for pyg_event in pygame.event.get():
            if pyg_event.type == QUIT:
                pygame.quit()

        if default.verbose:
            if circle.steps == 0 and not generation % 10:
                default.reset_screen()
                circle.draw_path(default, parent=True)
            circle.draw(default)

        move_limit = get_move_limit(generation, default, circle)

        if not circle.dead and circle.steps < move_limit:
            direction = get_direction(generation, circle, default)

            circle.move(direction, default)
            circle.steps += 1

            if circle.win:
                win_count += 1

                if not win_count % 5:
                    default.reset_screen()

                if default.verbose:
                    circle.draw_path(default)

                generation, best_count = circle.advance_generation(generation, win_count, best_count, default)
        else:
            generation, best_count = circle.advance_generation(generation, win_count, best_count, default)

    print(circle.parent)

    # Wait for user to close the PyGame screen
    while True:
        for pyg_event in pygame.event.get():
            if pyg_event.type == QUIT:
                pygame.quit()


def stop_simulation():
    pygame.quit()
    # sys.exit()


def setup_output(form):
    output_fields = ['Generation', 'Best Gen', 'Best Steps', 'Best Score']
    output_links = {}

    for field in output_fields:
        row = tk.Frame(form)
        label = tk.Label(row, width=22, text=field, anchor='w')
        entry = tk.Entry(row)
        entry.insert(0, '')
        row.pack(side=tk.TOP,
                 fill=tk.X,
                 padx=5,
                 pady=5)
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.RIGHT,
                   expand=tk.YES,
                   fill=tk.X)
        output_links[field] = entry

    return output_links

def acquire_ai_parameters():
    form_interface = tk.Tk()
    entries = makeform(form_interface, input_fields)

    output_links = setup_output(form_interface)

    start_button = tk.Button(form_interface, text='Start Simulation', command=(lambda e=entries: run_simulation(e, output_links)))
    start_button.pack(side=tk.LEFT, padx=5, pady=5)
    stop_button = tk.Button(form_interface, text='Stop Simulation', command=(lambda e=entries: stop_simulation(e)))
    stop_button.pack(side=tk.LEFT, padx=5, pady=5)
    quit_button = tk.Button(form_interface, text='Quit', command=form_interface.quit)
    quit_button.pack(side=tk.LEFT, padx=5, pady=5)

    form_interface.mainloop()

acquire_ai_parameters()
