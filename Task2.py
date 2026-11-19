"""Compare Task 1 with a GA that keeps each lecture's assignment together."""

from time import perf_counter

import numpy as np
import common


def crossover(parents, offspring_size, ga):
    # Cut between lectures so the time, room and teacher stay together.
    children = []
    for i in range(offspring_size[0]):
        first = parents[i % len(parents)]
        second = parents[(i + 1) % len(parents)]
        cut = 3 * ga.python_random_generator.randint(1, len(common.LECTURES))
        children.append(np.concatenate((first[:cut], second[cut:])))
    return np.array(children)


def mutation(children, ga):
    for child in children:
        gene = ga.python_random_generator.randrange(len(child))
        candidate = child.copy()
        candidate[gene] = ga.python_random_generator.choice(ga.gene_space[gene])
        if common.fitness_function(ga, candidate, 0) >= common.fitness_function(ga, child, 0):
            child[gene] = candidate[gene]
    return children


def run(label, **operators):
    # One timestamp per generation, at the end of each step.
    parents, crossed, mutated = [], [], []
    started = perf_counter()
    ga = common.create_ga(
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


@common.task_output()
def main():
    common.load_data()
    run("Task 1")
    run("Task 2", crossover_type=crossover, mutation_type=mutation)


if __name__ == "__main__":
    main()
