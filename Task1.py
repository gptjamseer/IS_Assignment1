"""Task 1: generate and display a one-day lecture schedule."""

import common


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


@common.task_output()
def main():
    common.load_data()
    ga = common.create_ga()
    ga.run()

    solution, fitness, _ = ga.best_solution(pop_fitness=ga.last_generation_fitness)
    schedule = common.decode_solution(solution)
    errors = common.evaluate_schedule(schedule)
    print(f"Best fitness: {fitness}")
    for name, count in errors.items():
        print(f"  {name}: {count}")
    print(f"  is_valid: {not any(errors.values())}")
    print_schedule(schedule)


if __name__ == "__main__":
    main()
