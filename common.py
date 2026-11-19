from pathlib import Path
from contextlib import contextmanager

import pygad


POPULATION_SIZE = 300
SEED = 12
BASE_DIR = Path(__file__).resolve().parent
LECTURES = []
CLASSROOMS = {}
TEACHERS = {}


def read_list_file(filename, folder=BASE_DIR):
    """Read lines written as: Name [value, value]."""
    result = {}
    with open(folder / filename, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            name, values = line.split("[", 1)
            result[name.strip()] = [
                value.strip() for value in values.rstrip("]").split(",")
            ]
    return result


def load_data(folder=BASE_DIR):
    """Load the three assignment input files."""
    global LECTURES, CLASSROOMS, TEACHERS
    classes = read_list_file("Classes.txt", folder)
    classroom_data = read_list_file("Classrooms.txt", folder)
    teacher_data = read_list_file("Teachers.txt", folder)

    lectures = []
    for subject, durations in classes.items():
        for number, duration in enumerate(durations, start=1):
            lectures.append(
                {
                    "id": f"{subject}-{number}",
                    "subject": subject,
                    "duration": int(duration),
                }
            )

    classrooms = {
        name: (int(hours[0]), int(hours[1]))
        for name, hours in classroom_data.items()
    }
    teachers = {
        name: {subject.lower() for subject in subjects}
        for name, subjects in teacher_data.items()
    }
    LECTURES, CLASSROOMS, TEACHERS = lectures, classrooms, teachers


def decode_solution(solution):
    """Convert groups of three genes into lecture assignments."""
    room_names = list(CLASSROOMS)
    teacher_names = list(TEACHERS)
    schedule = []

    for index, lecture in enumerate(LECTURES):
        start = int(solution[index * 3])
        room = room_names[int(solution[index * 3 + 1])]
        teacher = teacher_names[int(solution[index * 3 + 2])]
        schedule.append(
            {
                **lecture,
                "start": start,
                "end": start + lecture["duration"],
                "room": room,
                "teacher": teacher,
            }
        )
    return schedule


def overlap(first, second):
    """Check overlap between two half-open intervals [start, end)."""
    return first["start"] < second["end"] and second["start"] < first["end"]


def evaluate_schedule(schedule):
    """Count all Task 1 constraint violations."""
    result = {
        "invalid_teacher": 0,
        "unavailable_classroom": 0,
        "classroom_overlap": 0,
        "teacher_overlap": 0,
    }

    for lecture in schedule:
        if lecture["subject"].lower() not in TEACHERS[lecture["teacher"]]:
            result["invalid_teacher"] += 1

        room_start, room_end = CLASSROOMS[lecture["room"]]
        if lecture["start"] < room_start or lecture["end"] > room_end:
            result["unavailable_classroom"] += 1

    for index, first in enumerate(schedule):
        for second in schedule[index + 1 :]:
            if not overlap(first, second):
                continue

            if first["room"] == second["room"]:
                result["classroom_overlap"] += 1
            if first["teacher"] == second["teacher"]:
                result["teacher_overlap"] += 1

    return result


def fitness_function(ga_instance, solution, solution_idx):
    """Reward schedules with fewer constraint violations."""
    errors = evaluate_schedule(decode_solution(solution))
    return 10_000 - 600 * sum(errors.values())


def create_gene_space():
    """Give each lecture its possible start times, room indexes and teacher indexes."""
    first_hour = min(start for start, _ in CLASSROOMS.values())
    last_hour = max(end for _, end in CLASSROOMS.values())
    gene_space = []

    for lecture in LECTURES:
        starts = list(range(first_hour, last_hour - lecture["duration"] + 1))
        gene_space.extend(
            [
                starts,
                list(range(len(CLASSROOMS))),
                list(range(len(TEACHERS))),
            ]
        )
    return gene_space


def create_ga(**options):
    settings = dict(
        sol_per_pop=POPULATION_SIZE, 
        num_genes=3 * len(LECTURES),
        num_generations=800, 
        num_parents_mating=80, 
        random_seed=SEED,
        fitness_func=fitness_function, 
        gene_space=create_gene_space(),
        gene_type=int, 
        stop_criteria="reach_10000",
    )
    settings.update(options)
    return pygad.GA(**settings)
