"""Compare two ways to optimize teacher preferences and teaching hours."""

import json
import common
import Task2


def read_preferences():
    preferences = {}
    for line in (common.BASE_DIR / "Preferences.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            name, values = line.split("{", 1)
            preferences[name.strip()] = json.loads("{" + values.replace("“", '"').replace("”", '"'))
    return preferences


def measure(solution, preferences):
    schedule = common.decode_solution(solution)
    violations = sum(common.evaluate_schedule(schedule).values())
    hours = dict.fromkeys(common.TEACHERS, 0)
    liked = disliked = 0
    for lecture in schedule:
        teacher = lecture["teacher"]
        hours[teacher] += lecture["duration"]
        for hour in range(lecture["start"], lecture["end"]):
            start, end = preferences[teacher]["likes"]
            liked += start <= hour < end
            start, end = preferences[teacher]["dislikes"]
            disliked += start <= hour < end
    gap = max(hours.values()) - min(hours.values())
    return violations, liked, disliked, gap, hours


def compare():
    common.load_data()
    preferences = read_preferences()
    # Both methods start from the same population, including Task 2's best solution.
    warmup = common.create_ga(crossover_type=Task2.crossover, mutation_type=Task2.mutation)
    warmup.run()
    population = warmup.population[:64].copy()
    population[0] = warmup.best_solution(pop_fitness=warmup.last_generation_fitness)[0]
    total_hours = sum(lecture["duration"] for lecture in common.LECTURES)
    results = {}
    for method in ("Weighted sum", "NSGA-II"):
        def fitness(ga, solution, index):
            violations, liked, disliked, gap, _ = measure(solution, preferences)
            # One hard violation outweighs the full range of either soft score.
            penalty = (3 * total_hours + 1) * violations
            if method == "Weighted sum":
                return liked - disliked - gap - penalty
            return [liked - disliked - penalty, -gap - penalty]

        ga = common.create_ga(initial_population=population.copy(), fitness_func=fitness,
                              num_generations=80, num_parents_mating=16, stop_criteria=None,
                              parent_selection_type="sss" if method == "Weighted sum" else "nsga2")
        ga.run()
        rows = [measure(solution, preferences) for solution in ga.population]
        # Use the same tie-break to show one representative from each final population.
        best = max(rows, key=lambda r: (-r[0], r[1] - r[2] - r[3], -r[3]))
        results[method] = best
        violations, liked, disliked, gap, hours = best
        print(f"{method}: violations={violations}, liked={liked} h, disliked={disliked} h, gap={gap} h")
        print("  Teaching hours:", hours)
        if method == "NSGA-II":
            pairs = sorted({(l - d, g) for v, l, d, g, _ in rows if v == 0}, reverse=True)
            front = [(p, g) for p, g in pairs
                     if not any(q >= p and h <= g and (q, h) != (p, g) for q, h in pairs)]
            print("  Feasible trade-offs (net preference, gap):", front)
    return results


@common.task_output()
def main():
    compare()


if __name__ == "__main__":
    main()
    