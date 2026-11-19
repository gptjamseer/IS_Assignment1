"""Task 1: generate and display a one-day lecture schedule."""

import pygad
import common

POPULATION_SIZE = 300
SEED = 12


def decode_solution(solution):
    """Convert groups of three genes into lecture assignments."""
    room_names = list(common.CLASSROOMS)
    teacher_names = list(common.TEACHERS)
    schedule = []

    for index, lecture in enumerate(common.LECTURES):
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
        if lecture["subject"].lower() not in common.TEACHERS[lecture["teacher"]]:
            result["invalid_teacher"] += 1

        room_start, room_end = common.CLASSROOMS[lecture["room"]]
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
    first_hour = min(start for start, _ in common.CLASSROOMS.values())
    last_hour = max(end for _, end in common.CLASSROOMS.values())
    gene_space = []

    for lecture in common.LECTURES:
        starts = list(range(first_hour, last_hour - lecture["duration"] + 1))
        gene_space.extend(
            [
                starts,
                list(range(len(common.CLASSROOMS))),
                list(range(len(common.TEACHERS))),
            ]
        )
    return gene_space


def create_ga(**options):
    settings = dict(
        sol_per_pop=POPULATION_SIZE, 
        num_genes=3 * len(common.LECTURES),
        num_generations=800, 
        num_parents_mating=80, 
        random_seed=SEED,
        fitness_func=fitness_function, 
        gene_space=create_gene_space(),
        gene_type=int, 
    )
    settings.update(options)
    return pygad.GA(**settings)



def print_schedule(schedule):
    """Print the final schedule ordered by time and classroom."""
    schedule = sorted(schedule, key=lambda item: (item["start"], item["room"]))
    print(f"\n{'Start-End':<11} | {'Room':<4} | {'Subject':<16} | Teacher")
    for item in schedule:
        time = f"{item['start']:02d}:00-{item['end']:02d}:00"
        print(
            f"{time:<11} | {item['room']:<4} | "
            f"{item['subject']:<16} | {item['teacher']}"
        )


def main():
    common.load_data()
    ga = create_ga()
    ga.run()

    solution, fitness, _ = ga.best_solution(pop_fitness=ga.last_generation_fitness)
    schedule = decode_solution(solution)
    errors = evaluate_schedule(schedule)
    print(f"Best fitness: {fitness}")
    for name, count in errors.items():
        print(f"  {name}: {count}")
    print(f"  is_valid: {not any(errors.values())}")
    print_schedule(schedule)


if __name__ == "__main__":
    main()
