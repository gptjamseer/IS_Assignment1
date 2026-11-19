# Program Guide

This guide describes the current `common.py`, `Task1.py`–`Task4.py`, and `Task4.ipynb` implementation. Identifiers match the source files.

## 1. Purpose and execution flow

The program uses a Genetic Algorithm (GA) to construct and evaluate a university lecture schedule for one day. A solution represents one candidate timetable. A population contains multiple candidates. Each generation selects parents and produces candidates through crossover and mutation.

| Stage | Goal | Main operation |
|---|---|---|
| Task 1 | Find a schedule satisfying the basic constraints | Representation, constraint checks, fitness, basic PyGAD execution |
| Task 2 | Improve the search | Lecture-level crossover and mutation that does not increase violations |
| Task 3 | Optimize teacher preferences and workload balance | Compare Weighted sum and NSGA-II |
| Task 4 | Evaluate performance | Compare input size, difficulty, operators, and population size |
| Notebook | Inspect results | Execute each task and display fitness graphs |

```text
Input txt → common.load_data()
          → Task1.create_ga() → ga.run()
          → decode and evaluate → output

Task2 → attach custom operators to the Task1 GA
Task3 → prepare a population with Task2 operators → compare two objectives approaches
Task4 → four input cases × three configurations → twelve results
Notebook → run Tasks 1–4 → plot Task4 histories
```

Task 3 runs its own warm-up GA. It does not automatically reuse the result of the earlier Task 2 notebook cell. Task 4 also starts fresh runs for its experimental configurations.

## 2. Running the program and understanding the inputs

Run these commands from the project directory using the intended Python environment.

```bash
python -m pip install -r requirements.txt
python Task1.py
python Task2.py
python Task3.py
python Task4.py
```

Execute `Task4.ipynb` from top to bottom with the project directory as the kernel's working directory. The current file layout has no menu-based `main.py`.

| File | Example | Meaning |
|---|---|---|
| Classes.txt | `Programming [2, 3, 2]` | Three lectures lasting two, three, and two hours |
| Classrooms.txt | `P1 [10, 16]` | P1 is available from 10:00 to 16:00 |
| Teachers.txt | `Anna [Programming, Math]` | Subjects Anna is qualified to teach |
| Preferences.txt | `Anna {"likes": [10, 11], "dislikes": [12, 14]}` | Preferred and disliked hours, used by Task 3 |

Time intervals use `[start, end)` semantics. A 10:00–12:00 lecture can be followed by a 12:00–14:00 lecture without overlap. Times are integers and the model covers a single day.

| Case | Location | Lectures / rooms / teachers | Conditions |
|---|---|---|---|
| Small / Difficult | Project root | 10 / 4 / 4 | Supplied inputs with restricted availability and qualifications |
| Small / Easy | Task4_input/small_easy | 10 / 4 / 4 | 08:00–20:00, all teachers qualified for all subjects |
| Large / Easy | Task4_input/large_easy | 60 / 12 / 12 | 08:00–20:00, all teachers qualified for all subjects |
| Large / Difficult | Task4_input/large_difficult | 60 / 12 / 12 | 08:00–18:00, one qualified teacher per subject |

Easy and Difficult inputs of the same size share the same lecture list. All large-case lectures last two hours. A feasible Large / Difficult schedule can be constructed by assigning each subject its own room and qualified teacher, with starts at 08, 10, 12, 14, and 16. Failure within the generation budget does not establish that no valid schedule exists.

## 3. common.py — loading data

| Name | Responsibility |
|---|---|
| `BASE_DIR` | Absolute directory containing common.py |
| `LECTURES` | List of dictionaries describing individual lectures |
| `CLASSROOMS` | Dictionary mapping room names to `(start, end)` |
| `TEACHERS` | Dictionary mapping teacher names to sets of qualified subjects |
| `read_list_file(filename, folder=BASE_DIR)` | Parse `Name [value, value]` lines into a dictionary of string lists |
| `load_data(folder=BASE_DIR)` | Read the three inputs, convert numeric fields, and replace the shared data |

### Lines worth understanding

```python
BASE_DIR = Path(__file__).resolve().parent
```

`__file__` identifies the Python file. `resolve()` obtains its absolute path, and `parent` obtains the containing directory.

```python
name, values = line.split("[", 1)
```

Split once at the first opening bracket. The left side is the name and the right side contains the values. Subsequent `rstrip("]")`, `split(",")`, and `strip()` calls remove the closing bracket, separate values, and trim whitespace.

```python
for number, duration in enumerate(durations, start=1):
```

Read each duration together with a number starting at one. IDs such as `Programming-1` distinguish lectures belonging to the same subject.

`global LECTURES, CLASSROOMS, TEACHERS` lets the function replace module-level variables. Other tasks access them as `common.LECTURES`, so they see the newly loaded data. Teacher qualifications are stored as lowercase sets for membership checks. The parser assumes the specified input format.

## 4. Task1.py — the basic scheduling algorithm

### Solution representation

Each lecture occupies three genes.

```python
[start_time, classroom_index, teacher_index]
```

For N lectures, a solution has `3 * N` genes. The order in `common.LECTURES` determines which lecture each group represents, ensuring every lecture appears exactly once. Duration comes from the input.

### Every function

| Function | Responsibility and return value |
|---|---|
| `decode_solution(solution)` | Convert the numeric array into a list of scheduled lecture dictionaries |
| `overlap(first, second)` | Return True when two lecture intervals overlap |
| `evaluate_schedule(schedule)` | Return a dictionary containing four hard-constraint violation counts |
| `fitness_function(ga_instance, solution, solution_idx)` | Return `10000 - 600 × total violations` |
| `create_gene_space()` | Build the permitted value list for every gene |
| `create_ga(**options)` | Combine default settings with overrides and return a pygad.GA object |
| `print_schedule(schedule)` | Sort by start time and room and print the timetable |
| `main()` | Load data, execute the GA, evaluate its final best candidate, and print results |

### Important expressions

`solution[index * 3]`, `solution[index * 3 + 1]`, and `solution[index * 3 + 2]` read a lecture's start, room index, and teacher index. Room and teacher genes index the corresponding name lists.

```python
{**lecture, "start": start, "end": start + lecture["duration"], ...}
```

`**lecture` expands the existing lecture fields into a new dictionary. Assignment fields are then added.

```python
first["start"] < second["end"] and second["start"] < first["end"]
```

This is the overlap test. Strict inequalities allow one lecture to start when the other ends.

`schedule[index + 1:]` selects only later lectures, excluding self-comparisons and preventing double counting of A-B and B-A. A pair sharing both a teacher and a room can contribute two violations.

`range(first_hour, last_hour - duration + 1)` includes the latest permitted start because Python excludes the upper range bound. The bounds use the earliest opening and latest closing across all rooms. Fitness checks whether the selected individual room is available.

```python
def create_ga(**options):
    settings = dict(...)
    settings.update(options)
    return pygad.GA(**settings)
```

In the definition, `**options` collects keyword arguments into a dictionary. `update()` replaces specified defaults. In the call, `**settings` expands dictionary entries into keyword arguments.

Defaults are 300 candidates, 800 generations, 80 mating parents, seed 12, and integer genes. There is no default early termination on success. Other tasks override the settings they need.

`ga.best_solution(pop_fitness=ga.last_generation_fitness)` uses the final population's fitness values to obtain its best candidate. It returns solution, fitness, and index. `_` receives the unused index. `not any(errors.values())` is True only when all violation counts are zero.

### Output fields

| Output | Meaning |
|---|---|
| Best fitness | Score of the returned best timetable; 10000 means zero violations |
| invalid_teacher | Lectures assigned to teachers lacking the required qualification |
| unavailable_classroom | Lectures outside their assigned room's availability |
| classroom_overlap | Overlapping lecture pairs assigned to the same room |
| teacher_overlap | Overlapping lecture pairs assigned to the same teacher |
| is_valid | True when no constraint violations remain |
| Start-End / Room / Subject / Teacher | Time interval, room, subject, and assigned teacher |

A score of 9400 means one violation. A score of -14000 means 40 violations. Scores become negative at 17 violations. Higher is better.

## 5. Task2.py — custom operators

| Function | Responsibility and return value |
|---|---|
| `crossover(parents, offspring_size, ga)` | Combine parent slices at lecture boundaries and return a NumPy offspring array |
| `lecture_errors(solution, index)` | Count qualification, availability, and pairwise conflict violations involving one lecture |
| `mutation(children, ga)` | Try one gene change per offspring; accept when violations do not increase; return the array |
| `run(label, **operators)` | Execute a GA, print timing and fitness changes, and return fitness history |
| `main()` | Load the supplied inputs and run the Custom GA once |

### Crossover

`i % len(parents)` and `(i + 1) % len(parents)` cycle through adjacent parents, wrapping around at the end of the parent list.

```python
cut = 3 * ga.python_random_generator.randint(1, len(common.LECTURES))
np.concatenate((first[:cut], second[cut:]))
```

Multiplying by three keeps each lecture's genes together. The first parent provides the prefix and the second provides the suffix. `randint` includes both bounds, so choosing the final boundary produces a copy of the first parent. This operator does not guarantee qualification or conflict feasibility.

### Mutation

`candidate = child.copy()` makes a trial copy. `randrange` selects one gene position, and `choice(ga.gene_space[gene])` selects a permitted value. The sampled value can equal the old value.

`gene // 3` identifies the lecture containing the gene. For example, genes 6, 7, and 8 all belong to lecture index 2.

```python
if lecture_errors(candidate, lecture_index) <= lecture_errors(child, lecture_index):
    child[gene] = candidate[gene]
```

The mutation is accepted when violations stay equal or decrease. Only one lecture changes, so violations involving exclusively other lectures remain constant. Under the current Task 1 fitness, this gives the same acceptance decision as reevaluating the entire timetable. The check scans O(N) affected pairs instead of all O(N²) pairs. Decoding the schedule is also O(N).

`errors += condition` relies on True counting as one and False as zero. `other_index != index` excludes the lecture itself.

### Timing and output

The `on_parents`, `on_crossover`, and `on_mutation` callbacks record completion timestamps. `lambda ga, _: ...` defines a short callback whose second argument is unused. Random choices use the GA's random generator.

`np.subtract(crossed, parents)` subtracts parent-selection completion from crossover completion. Mutation uses the same approach. Multiplying the mean by 1000 converts seconds to milliseconds. These are intervals between callbacks and include small callback overheads.

| Output | Meaning |
|---|---|
| Task 2 (... s) | Total GA construction and execution time |
| crossover: ... ms/generation | Average crossover interval for all offspring in a generation |
| mutation: ... ms/generation | Average mutation interval for all offspring in a generation |
| Generation g: best fitness f | Best fitness at generation g, printed initially and whenever it changes |

Generation zero describes the initial population. The last printed generation need not be the termination generation. Unchanged fitness produces no further history lines.

## 6. Task3.py — teacher preferences and balance

| Function | Responsibility and return value |
|---|---|
| `read_preferences()` | Parse Preferences.txt into teacher likes/dislikes dictionaries |
| `measure(solution, preferences)` | Return `(violations, liked, disliked, gap, hours)` |
| `starting_population()` | Run a warm-up with Task 2 operators, take 64 final candidates, and put the warm-up best candidate first |
| `result_priority(result)` | Return a ranking key for selecting the displayed representative |
| `run(method, population, preferences)` | Run the selected optimization method and return the representative's measurements |
| Nested `fitness(ga, solution, index)` | Return one scalar for Weighted sum or a two-objective list for NSGA-II |
| `compare()` | Run both methods from the same initial population, print results, and return a dictionary keyed by method |
| `main()` | Execute compare() |

### Measuring preferences and balance

`json.loads("{" + values.replace(...))` normalizes curly quotation marks and parses the preference dictionary.

`dict.fromkeys(common.TEACHERS, 0)` initializes every teacher's assigned hours to zero. Teachers with no assignments remain included in balance calculations.

Each integer hour of a lecture contributes one to `liked` when inside the teacher's likes interval and one to `disliked` when inside the dislikes interval. A 10:00–12:00 lecture overlapping likes `[10, 11]` contributes one liked hour. The two conditions are checked independently.

```python
gap = max(hours.values()) - min(hours.values())
```

The workload gap is the difference between the most and least assigned teaching hours. Smaller values indicate better balance.

### Two optimization methods

```python
preference = liked - disliked
penalty = (3 * total_hours + 1) * violations

# Weighted sum
return preference - gap - penalty

# NSGA-II
return [preference - penalty, -gap - penalty]
```

Weighted sum combines both objectives and uses `sss` parent selection. NSGA-II keeps separate objective scores and uses `nsga2` selection. NSGA-II stands for Non-dominated Sorting Genetic Algorithm II. It can retain candidates that are better on one objective and worse on another.

For total lecture hours H, preference lies between -H and H, while gap lies between zero and H. The `3*H+1` penalty therefore prevents a hard violation from being offset by soft-score gains. Task 3 fitness uses a different scale from Task 1's 10000-point score.

Both methods receive a `.copy()` of the same 64 initial candidates and run for 80 generations with 16 parents and seed 12. Their main optimization runs use PyGAD's default crossover and mutation. Task 2's custom operators are used in the warm-up.

```python
return -violations, liked - disliked - gap, -gap
```

`max(rows, key=result_priority)` compares these tuples from left to right. It prioritizes fewer violations, then larger preference-minus-gap, then a smaller gap. This same rule selects one representative from the NSGA-II run. The output does not enumerate its entire Pareto front.

### Output fields

| Output | Meaning |
|---|---|
| Weighted sum, NSGA-II | Optimization method used |
| violations | Number of hard-constraint violations |
| liked | Total teaching hours assigned within preferred intervals |
| disliked | Total teaching hours assigned within disliked intervals |
| gap | Difference between maximum and minimum teacher workload |
| Teaching hours | Dictionary of total assigned hours per teacher |

For `liked=10 h, disliked=4 h, gap=3 h`, preference is six. With zero hard violations, Weighted sum fitness is three. Matching printed representatives do not establish that the algorithms behave identically throughout the search.

## 7. Task4.py — experiments and measurements

| Function | Responsibility and return value |
|---|---|
| `run_case(case, method, population)` | Execute one GA on the currently loaded data and return a measurement dictionary |
| Nested `record_fitness(ga, fitness)` | Record the generation and time of the first observed valid solution |
| `experiment()` | Print twelve runs across four cases and three configurations; return a list of result dictionaries |
| `main()` | Execute experiment() |

Each case runs Default/60, Custom/60, and Custom/120. Comparing the first two isolates the operator configuration. Comparing the two Custom runs changes population size. Every run uses 16 parents, seed 12, and 100 generations.

### Important expressions

`nonlocal first_valid, time_to_valid` lets the nested callback update variables in the enclosing `run_case()` call.

```python
if first_valid is None and max(fitness) >= 10_000:
```

Only the first observation of a valid candidate is recorded. Later successful populations do not overwrite it. Generation zero is possible if the initial population is already feasible. Timing starts before GA construction and ends at the population-fitness callback, including setup and evaluation time.

`stop_criteria=None` keeps the run going through all 100 generations. First-success time and total execution time are therefore stored separately.

`zip(parents, crossed)` pairs completion times from matching generations. `mean(end - start for ...)` calculates their average interval.

`try ... finally` restores the root input data even if an experiment raises an error. It does not modify the input files.

### Printed columns and result dictionary

| Printed column | Dictionary key | Meaning |
|---|---|---|
| Input | case | Input case |
| Method | method | Default or Custom |
| Pop | population | Number of timetable candidates per generation |
| First gen | first_valid | First observed valid generation; None on failure |
| Time to valid(s) | time_to_valid | Seconds until first observed success; None on failure, displayed as Not found |
| Total(s) | total_time | Setup and full 100-generation execution time |
| Cross(ms/gen) | crossover_ms | Mean crossover interval per generation |
| Mutation(ms/gen) | mutation_ms | Mean mutation interval per generation |
| Best | best | Best fitness in the final history entry |
| Plot data | history | Best fitness history beginning with the initial population |

A failed run's Total is not a time to success. Task 4 reports one seed, and runtime depends on the environment and machine load. Failure on Large / Difficult means that the run did not find a valid schedule within its budget.

## 8. Task4.ipynb — results and plots

The first four cells execute Tasks 1, 2, 3, and 4. The final cell prepares plotting data from `runs`.

Current Task 4 results are dictionaries. An earlier version returned tuples of `(case, method, population, first_valid, elapsed, history)`. `isinstance(row, dict)` identifies the format. Old tuples are unpacked and converted to plotting dictionaries so existing kernel data can still be plotted.

```python
cases = list(dict.fromkeys(row["case"] for row in plot_rows))
```

The generator supplies each case name. Dictionary keys remove duplicates while retaining first appearance order, and list converts those keys to the four case names.

`plt.subplots(2, 2, ..., sharex=True)` creates four axes with a shared horizontal scale. `axes.flat` iterates through the two-dimensional axes array. `zip(cases, axes.flat)` associates each case with one plot.

`ax.step(..., where="post")` displays each generation's value until the next generation. `fig.tight_layout()` adjusts spacing to avoid overlapping labels.

| Plot element | Meaning |
|---|---|
| Title | Small/Large and Easy/Difficult combination |
| Generation | Generation number; zero is the initial population |
| Best fitness | Best score at that generation; higher is better |
| Default / 60, etc. | Operator configuration and population size |
| Reaching 10000 | A candidate with zero hard violations was found |

Vertical scales are automatically chosen per panel, while the horizontal scale is shared. Compare numeric values when comparing different panels.

Python caches imported modules in the kernel. After changing `.py` files, restart the kernel and run cells in order if results remain outdated or formats disagree. Stored outputs reflect the last execution and do not update automatically when source files change.

## 9. Shared Python idioms and interpretation notes

| Expression | Meaning |
|---|---|
| `if __name__ == "__main__":` | Run the main function when the file is executed directly |
| `**operators` | Expand dictionary entries into keyword arguments |
| `.copy()` | Separate trial changes or independent runs from the original array |
| `lambda` | Short anonymous function used for callbacks and sorting |
| `f"{value:.3f}"` | Display three decimal places |
| `f"{value:>9}"` | Right-align in a field nine characters wide |
| `None` | Missing measurement or no successful solution in that run |

Tasks 1 and 2 use the default 800-generation budget without stopping at first success. Task 3 runs an additional 80-generation comparison after warm-up. Task 4 uses fresh runs with a 100-generation budget, so its success generations can differ from standalone Task 2 results.

`lecture_errors()` implements the same hard-constraint rules as Task 1. Adding constraints requires reviewing the partial mutation check as well. Task 2 mutation is designed for the hard-constraint fitness; reusing it directly for Task 3's soft objectives requires checking its acceptance rule.
