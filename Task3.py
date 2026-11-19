"""Compare two ways to optimize teacher preferences and teaching hours."""

import json
import common
import Task1
import Task2


def read_preferences():
    preferences = {}
    for line in (common.BASE_DIR / "Preferences.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            name, values = line.split("{", 1)
            preferences[name.strip()] = json.loads("{" + values.replace("“", '"').replace("”", '"'))
    return preferences


def measure(solution, preferences):
    schedule = Task1.decode_solution(solution)
    violations = sum(Task1.evaluate_schedule(schedule).values())
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


def starting_population():
    # Both methods start from the same population, including Task 2's best solution.
    warmup = Task1.create_ga(crossover_type=Task2.crossover, mutation_type=Task2.mutation)
    warmup.run()
    population = warmup.population[:64].copy()
    population[0] = warmup.best_solution(pop_fitness=warmup.last_generation_fitness)[0]
    return population


def result_priority(result):
    violations, liked, disliked, gap, _ = result
    return -violations, liked - disliked - gap, -gap


def run(method, population, preferences):
    total_hours = sum(lecture["duration"] for lecture in common.LECTURES)

    def fitness(ga, solution, index):
        violations, liked, disliked, gap, _ = measure(solution, preferences)
        # Keep hard constraints more important than either soft objective.
        penalty = (3 * total_hours + 1) * violations
        preference = liked - disliked
        if method == "Weighted sum":
            return preference - gap - penalty
        return [preference - penalty, -gap - penalty]

    ga = Task1.create_ga(
        initial_population=population.copy(), fitness_func=fitness,
        num_generations=80, num_parents_mating=16, stop_criteria=None,
        parent_selection_type="sss" if method == "Weighted sum" else "nsga2",
    )
    ga.run()
    rows = [measure(solution, preferences) for solution in ga.population]
    # Select one representative using the same rule for both methods.
    return max(rows, key=result_priority)


def compare():
    common.load_data()
    preferences = read_preferences()
    population = starting_population()
    results = {}
    for method in ("Weighted sum", "NSGA-II"):
        best = run(method, population, preferences)
        results[method] = best
        violations, liked, disliked, gap, hours = best
        print(f"{method}: violations={violations}, liked={liked} h, disliked={disliked} h, gap={gap} h")
        print("  Teaching hours:", hours)
    return results


def main():
    compare()


if __name__ == "__main__":
    main()
    
