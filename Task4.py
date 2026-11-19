"""Compare input cases, search operators and population sizes."""

from time import perf_counter
from statistics import mean

import common
import Task1
import Task2


def run_case(case, method, population):
    parents, crossed, mutated = [], [], []
    first_valid = None
    time_to_valid = None

    def record_fitness(ga, fitness):
        nonlocal first_valid, time_to_valid
        if first_valid is None and max(fitness) >= 10_000:
            first_valid = ga.generations_completed
            time_to_valid = perf_counter() - started

    operators = {}
    if method == "Custom":
        operators = dict(crossover_type=Task2.crossover, mutation_type=Task2.mutation)

    started = perf_counter()
    ga = Task1.create_ga(
        sol_per_pop=population, num_parents_mating=16, num_generations=100,
        stop_criteria=None, on_fitness=record_fitness,
        on_parents=lambda ga, _: parents.append(perf_counter()),
        on_crossover=lambda ga, _: crossed.append(perf_counter()),
        on_mutation=lambda ga, _: mutated.append(perf_counter()),
        **operators,
    )
    ga.run()
    elapsed = perf_counter() - started
    history = list(ga.best_solutions_fitness)
    return dict(
        case=case, method=method, population=population,
        first_valid=first_valid, time_to_valid=time_to_valid, total_time=elapsed,
        crossover_ms=mean(end - start for start, end in zip(parents, crossed)) * 1000,
        mutation_ms=mean(end - start for start, end in zip(crossed, mutated)) * 1000,
        best=history[-1], history=history,
    )


def experiment():
    cases = {
        "Small / Easy": "Task4_input/small_easy",
        "Small / Difficult": ".",
        "Large / Easy": "Task4_input/large_easy",
        "Large / Difficult": "Task4_input/large_difficult",
    }
    results = []
    print(f"{'Input':19} {'Method':8} {'Pop':>4} {'First gen':>9} "
          f"{'Time to valid(s)':>16} {'Total(s)':>9} {'Cross(ms/gen)':>14} "
          f"{'Mutation(ms/gen)':>17} {'Best':>8}")
    try:
        for case, folder in cases.items():
            common.load_data(common.BASE_DIR / folder)
            for method, population in [("Default", 60), ("Custom", 60), ("Custom", 120)]:
                result = run_case(case, method, population)
                results.append(result)
                valid_time = result["time_to_valid"]
                time_text = "Not found" if valid_time is None else f"{valid_time:.3f}"
                print(f"{case:19} {method:8} {population:4} "
                      f"{str(result['first_valid']):>9} {time_text:>16} "
                      f"{result['total_time']:9.3f} {result['crossover_ms']:14.3f} "
                      f"{result['mutation_ms']:17.3f} {result['best']:8.0f}")
    finally:
        common.load_data()
    return results


def main():
    experiment()


if __name__ == "__main__":
    main()
