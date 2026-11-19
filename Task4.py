"""Run the input and parameter comparisons used in the seminar notebook."""

from time import perf_counter
import common
import Task2


def experiment():
    cases = {"Small / easy": "experiments/small_easy", "Small / supplied": ".",
             "Large / easy": "experiments/large_easy", "Large / tight": "experiments/large_tight"}
    results = []
    for case, folder in cases.items():
        common.load_data(common.BASE_DIR / folder)
        for method, population in [("Default", 60), ("Custom", 60), ("Custom", 120)]:
            operators = {} if method == "Default" else dict(
                crossover_type=Task2.crossover, mutation_type=Task2.mutation)
            start = perf_counter()
            ga = common.create_ga(sol_per_pop=population, num_parents_mating=16,
                                  num_generations=100, **operators)
            ga.run()
            elapsed = perf_counter() - start
            history = list(ga.best_solutions_fitness)
            first_valid = history.index(10_000) if 10_000 in history else None
            results.append((case, method, population, first_valid, elapsed, history))
            print(f"{case:18} {method:8} pop={population:3}  first valid={str(first_valid):4}"
                  f"  run={elapsed:.3f} s  best={history[-1]}")
    common.load_data()
    return results


@common.task_output()
def main():
    experiment()


if __name__ == "__main__":
    main()
