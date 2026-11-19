"""Run a GA that keeps each lecture's assignment together."""

from time import perf_counter

import numpy as np
import common
import Task1


def crossover(parents, offspring_size, ga):
    # Cut between lectures so the time, room and teacher stay together.
    children = []
    for i in range(offspring_size[0]):
        first = parents[i % len(parents)]
        second = parents[(i + 1) % len(parents)]
        cut = 3 * ga.python_random_generator.randint(1, len(common.LECTURES))
        children.append(np.concatenate((first[:cut], second[cut:])))
    return np.array(children)


def lecture_errors(solution, index):
    """Count only violations involving the lecture being changed."""
    schedule = Task1.decode_solution(solution)
    lecture = schedule[index]
    errors = int(lecture["subject"].lower() not in common.TEACHERS[lecture["teacher"]])
    room_start, room_end = common.CLASSROOMS[lecture["room"]]
    errors += lecture["start"] < room_start or lecture["end"] > room_end
    for other_index, other in enumerate(schedule):
        if other_index != index and Task1.overlap(lecture, other):
            errors += lecture["room"] == other["room"]
            errors += lecture["teacher"] == other["teacher"]
    return errors


def mutation(children, ga):
    for child in children:
        gene = ga.python_random_generator.randrange(len(child))
        candidate = child.copy()
        candidate[gene] = ga.python_random_generator.choice(ga.gene_space[gene])
        # Other lectures' violations are unchanged, so compare only this lecture.
        lecture_index = gene // 3
        if lecture_errors(candidate, lecture_index) <= lecture_errors(child, lecture_index):
            child[gene] = candidate[gene]
    return children


def run(label, **operators):
    # One timestamp per generation, at the end of each step.
    parents, crossed, mutated = [], [], []
    started = perf_counter()
    ga = Task1.create_ga(
        **operators,
        on_parents=lambda ga, _: parents.append(perf_counter()),
        on_crossover=lambda ga, _: crossed.append(perf_counter()),
        on_mutation=lambda ga, _: mutated.append(perf_counter()),
    )
    ga.run()
    print(f"{label} ({perf_counter() - started:.3f} s)")
    print(f"  crossover: {np.mean(np.subtract(crossed, parents)) * 1000:.2f} ms/generation")
    print(f"  mutation: {np.mean(np.subtract(mutated, crossed)) * 1000:.2f} ms/generation")
    history = ga.best_solutions_fitness
    for generation, fitness in enumerate(history):
        if generation == 0 or fitness != history[generation - 1]:
            print(f"  Generation {generation}: best fitness {fitness}")
    return history


def main():
    common.load_data()
    run("Task 2", crossover_type=crossover, mutation_type=mutation)


if __name__ == "__main__":
    main()
