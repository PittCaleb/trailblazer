import random
import locale
import json
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

OBSTACLES = '{"type": "Circle", "params": "(125, 400, 50)"}, {"type": "Circle", "params": "(200, 200, 75)"}, {"type": "Box", "params": "(450, 75, 100, 200)"}'

STEP_DISTANCE = 2
CIRCLE_SIZE = 2

INPUT_TEXT = 1
INPUT_RADIO = 2
INPUT_BOX = 3

input_fields = {'Start Pos': {'type': INPUT_TEXT, 'default': '(0, {})'.format(HEIGHT)},
                'Goal': {'type': INPUT_TEXT, 'default': str(GOAL)},
                'Output': {'type': INPUT_RADIO, 'options': {'Terse': True, 'Verbose': False}},
                'Generations': {'type': INPUT_TEXT, 'default': GENERATIONS},
                'Max Moves': {'type': INPUT_TEXT, 'default': MAX_MOVES},
                'Win Threshold': {'type': INPUT_TEXT, 'default': WIN_THRESHOLD},
                'Mutation Rate': {'type': INPUT_TEXT, 'default': MUTATION_RATE},
                'Obstacles': {'type': INPUT_BOX, 'default': OBSTACLES},
                'Splits': {'type': INPUT_TEXT, 'default': SPLITS},
                'Mutation Freedom': {'type': INPUT_TEXT, 'default': MUTATION_FREEDOM}}


def make_form(root, fields):
    entry_fields = {}

    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=22, text=field + ": ", anchor='w')

        if fields[field]['type'] == INPUT_TEXT:
            ent = tk.Entry(row)
            ent.insert(0, fields[field]['default'])
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        elif fields[field]['type'] == INPUT_RADIO:
            v = tk.StringVar()
            v.set('')  # initialize
            for label in fields[field]['options']:
                ent = tk.Radiobutton(row, text=label, variable=v, value=label)
                if fields[field]['options'][label]:
                    ent.select()
                ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
                entry_fields[field] = v
        elif fields[field]['type'] == INPUT_BOX:
            ent = tk.Text(row, width=49, height=4)
            ent.insert('1.0', fields[field]['default'])
            ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)

        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        if field not in entry_fields:
            entry_fields[field] = ent
    return entry_fields


def setup_output(form):
    output_labels = ['Generation', 'Best Gen', 'Best Steps', 'Best Score']
    output_fields = {}

    row = tk.Frame(form)
    label = tk.Label(row, width=22, text='Simulation Results:', anchor='w')
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    label.pack(side=tk.LEFT)

    for field in output_labels:
        row = tk.Frame(form)
        label = tk.Label(row, width=22, text=field, anchor='w')
        entry = tk.Entry(row)
        entry.insert(0, '')
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        label.pack(side=tk.LEFT)
        entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        output_fields[field] = entry

    return output_fields


def setup_path_box(form):
    row = tk.Frame(form)
    label = tk.Label(row, width=22, text='Simulation Path:', anchor='w')
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    label.pack(side=tk.LEFT)

    path_box = tk.Text(form, width=60, height=5)
    path_box.insert('1.0', '')
    path_box.pack()

    return path_box


def setup_buttons(form, entry_fields, output_fields, path_box):
    start_button = tk.Button(form, text='Start Simulation',
                             command=(lambda e=entry_fields: run_simulation(e, output_fields)))
    start_button.pack(side=tk.LEFT, padx=5, pady=5)

    path_button = tk.Button(form, text='Plot Path',
                            command=(lambda e=entry_fields, p=path_box: run_simulation(e, output_fields, p)))
    path_button.pack(side=tk.LEFT, padx=5, pady=5)

    stop_button = tk.Button(form, text='Stop Simulation', command=stop_simulation())
    stop_button.pack(side=tk.LEFT, padx=5, pady=5)

    quit_button = tk.Button(form, text='Quit', command=form.quit)
    quit_button.pack(side=tk.LEFT, padx=5, pady=5)


def draw_path(path, default):
    path_circle = Circle(Color().BLUE, CIRCLE_SIZE, default)
    path_circle.history = path
    path_circle.draw_path(default)


def convert_string_into_tuple(str):
    x, y = str.replace('(', '').replace(')', '').split(',')
    return (int(x), int(y))


def set_values_from_form(entry_fields, output_fields):
    for entry in entry_fields:
        entry_key = entry
        if entry_key != 'Obstacles':
            value = entry_fields[entry].get()

        if entry_key == 'Start Pos':
            start_position = convert_string_into_tuple(value)

        if entry_key == 'Goal':
            goal = convert_string_into_tuple(value)

        if entry_key == 'Output':
            if value.lower() == 'verbose':
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
            value = entry_fields[entry].get('1.0', tk.END)
            obstacle_array = '{"obstacles": [' + value + ']}'
            obstacles = json.loads(obstacle_array)

            for obstacle in obstacles['obstacles']:
                if obstacle['type'] == 'Box':
                    left, top, width, height = obstacle['params'].replace('(', '').replace(')', '').split(',')
                    obstacle['params'] = (int(left), int(top), int(width), int(height))
                if obstacle['type'] == 'Circle':
                    x, y, radius = obstacle['params'].replace('(', '').replace(')', '').split(',')
                    obstacle['params'] = (int(x), int(y), int(radius))

        if entry_key == 'Splits':
            splits = int(value)

        if entry_key == 'Mutation Freedom':
            mutation_freedom = int(value)

    direction_degrees = 359  # Not user settable, but needs stored in default

    print(
        'Initating Simulation with:\nstart_position={}, goal={}, verbose={}, generations={}, max_moves={}, win_threshold={}, mutation_rate={}, obstacles={}, splits={}'.format(
            start_position, goal, verbose, generations, max_moves, win_threshold, mutation_rate, obstacles, splits))

    return Default(start_position=start_position, goal=goal, verbose=verbose, generations=generations,
                   max_moves=max_moves, win_threshold=win_threshold, mutation_rate=mutation_rate, obstacles=obstacles,
                   splits=splits, width=WIDTH, height=HEIGHT, direction_degrees=direction_degrees,
                   mutation_freedom=mutation_freedom, step_distance=STEP_DISTANCE, circle_size=CIRCLE_SIZE,
                   output_fields=output_fields)


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


def run_simulation(entry_fields, output_fields, path=None):
    default = set_values_from_form(entry_fields, output_fields)
    default = initialize_pygame(default)

    if path:
        plot_path(path, default)
    else:
        doit(default)

    end_pygame()


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


def end_pygame():
    # Wait for user to close the PyGame screen
    while True:
        for pyg_event in pygame.event.get():
            if pyg_event.type == QUIT:
                pygame.quit()


def clean_path_data(path_string):
    path = path_string.get('1.0', tk.END)
    path = path.strip().replace('(', '').replace(')', '').replace('[', '').replace(']', '')
    path = path.split(',')
    path = [int(x.strip()) for x in path]
    return path


def plot_path(path_field, default):
    path = clean_path_data(path_field)
    plot_circle = Circle(Color().BLUE, CIRCLE_SIZE, default)
    plot_circle.history = path
    plot_circle.draw_path(default)


def stop_simulation():
    pygame.quit()
    # sys.exit()


def acquire_ai_parameters():
    form_interface = tk.Tk()

    entry_fields = make_form(form_interface, input_fields)
    output_fields = setup_output(form_interface)
    path_box = setup_path_box(form_interface)
    setup_buttons(form_interface, entry_fields, output_fields, path_box)

    form_interface.mainloop()


acquire_ai_parameters()
