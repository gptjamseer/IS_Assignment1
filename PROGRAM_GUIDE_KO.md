# 프로그램 설명서

현재 `common.py`, `Task1.py`~`Task4.py`, `Task4.ipynb`를 기준으로 작성한 설명서입니다. 코드의 식별자와 주요 알고리즘 용어는 영어로 표기합니다.

## 1. 목적과 전체 흐름

이 프로그램은 Genetic Algorithm(GA)을 이용해 하루 동안의 대학 강의 시간표를 생성하고 평가합니다. 시간표 후보 하나가 solution이고, 여러 후보의 집합이 population입니다. 각 generation에서 부모를 선택하고 crossover와 mutation으로 새로운 후보를 만들어 탐색합니다.

| 단계 | 목표 | 핵심 동작 |
|---|---|---|
| Task 1 | 기본 constraints를 만족하는 시간표 탐색 | 표현 방식, 제약 검사, fitness, 기본 PyGAD 실행 |
| Task 2 | 탐색 방식 개선 | 강의 단위 crossover, 위반 수를 늘리지 않는 mutation |
| Task 3 | 교사 preferences와 balance 최적화 | Weighted sum과 NSGA-II 비교 |
| Task 4 | 알고리즘 성능 평가 | 입력 크기·난이도·연산자·population 크기 비교 |
| Notebook | 결과 확인 | 각 Task 실행 및 fitness 그래프 표시 |

실행 흐름은 다음과 같습니다.

```text
입력 txt → common.load_data()
         → Task1.create_ga() → ga.run()
         → 해석·평가 → 결과 출력

Task2 → Task1의 기본 GA에 custom crossover/mutation 연결
Task3 → Task2 방식으로 초기 집단 준비 → 두 목적함수 방식 비교
Task4 → 4개 입력 집단 × 3개 설정 → 결과 12개
Notebook → Task 1, 2, 3, 4 실행 → Task 4 그래프
```

Notebook의 앞선 Task 2 실행 결과를 Task 3이 자동으로 가져오는 구조는 아닙니다. Task 3은 자체적으로 warm-up GA를 실행합니다. Task 4도 각 조건을 새로 실행합니다.

## 2. 실행 방법과 데이터

프로젝트 폴더에서 필요한 패키지를 설치하고 원하는 Task를 실행합니다.

```bash
python Task1.py
python Task2.py
python Task3.py
python Task4.py
```

`Task4.ipynb`는 프로젝트 폴더를 작업 위치로 사용하는 Python kernel에서 위에서 아래로 실행합니다. 현재 파일 구성에는 메뉴용 `main.py`가 없습니다.

| 파일 | 예시 | 의미 |
|---|---|---|
| Classes.txt | `Programming [2, 3, 2]` | 해당 과목에 2시간, 3시간, 2시간 강의가 각각 존재 |
| Classrooms.txt | `P1 [10, 16]` | P1 사용 가능 시간이 10시부터 16시까지 |
| Teachers.txt | `Anna [Programming, Math]` | Anna가 담당할 수 있는 과목 |
| Preferences.txt | `Anna {"likes": [10, 11], "dislikes": [12, 14]}` | 선호 시간과 비선호 시간. Task 3에서 사용 |

시간 구간은 `[start, end)`로 해석합니다. 10~12시 강의와 12~14시 강의는 겹치지 않습니다. 시간은 정수 단위이며 강의가 여러 날짜에 걸치는 모델은 구현되어 있지 않습니다.

| 실험 집단 | 위치 | 강의 / 강의실 / 교사 | 조건 |
|---|---|---|---|
| Small / Difficult | 프로젝트 루트 | 10 / 4 / 4 | 제공된 입력, 제한된 운영시간과 교사 자격 |
| Small / Easy | Task4_input/small_easy | 10 / 4 / 4 | 08~20시, 모든 교사가 모든 과목 담당 가능 |
| Large / Easy | Task4_input/large_easy | 60 / 12 / 12 | 08~20시, 모든 교사가 모든 과목 담당 가능 |
| Large / Difficult | Task4_input/large_difficult | 60 / 12 / 12 | 08~18시, 과목별 담당 교사 한 명 |

같은 크기의 Easy/Difficult는 동일한 강의 목록을 사용합니다. Large의 강의는 모두 2시간입니다. Large / Difficult는 각 과목에 방 하나와 담당 교사 한 명을 배정하고 08, 10, 12, 14, 16시에 강의를 시작하면 유효한 시간표를 구성할 수 있습니다. 제한 세대 안에서 GA가 실패하더라도 해의 부재를 뜻하지는 않습니다.

## 3. common.py — 데이터 로딩

| 이름 | 기능 |
|---|---|
| `BASE_DIR` | `common.py`가 위치한 폴더의 절대 경로 |
| `LECTURES` | 개별 강의를 나타내는 dictionary들의 list |
| `CLASSROOMS` | 강의실 이름을 `(start, end)`에 연결하는 dictionary |
| `TEACHERS` | 교사 이름을 담당 가능 과목들의 set에 연결하는 dictionary |
| `read_list_file(filename, folder=BASE_DIR)` | `Name [value, value]` 형식의 파일을 읽어 문자열 list를 값으로 갖는 dictionary 반환 |
| `load_data(folder=BASE_DIR)` | 세 입력 파일을 읽고 시간은 정수로 변환한 뒤 전역 데이터 세 개를 갱신 |

### 읽기 어려운 코드

```python
BASE_DIR = Path(__file__).resolve().parent
```

`__file__`은 현재 Python 파일 경로입니다. `resolve()`는 절대 경로를 얻고 `parent`는 파일을 담은 폴더를 얻습니다.

```python
name, values = line.split("[", 1)
```

첫 번째 `[`에서 한 번만 나눕니다. 왼쪽은 이름, 오른쪽은 값 목록입니다. 이후 `rstrip("]")`, `split(",")`, `strip()`으로 닫는 괄호와 불필요한 공백을 정리합니다.

```python
for number, duration in enumerate(durations, start=1):
```

강의 시간과 함께 1부터 시작하는 번호를 얻습니다. 같은 과목의 강의를 `Programming-1`, `Programming-2`처럼 구분합니다.

`global LECTURES, CLASSROOMS, TEACHERS`는 함수 안에서 모듈의 데이터 변수를 새 값으로 교체하기 위해 사용합니다. 다른 Task는 `common.LECTURES`처럼 접근하므로 입력 폴더를 바꾸면 갱신된 데이터를 봅니다. 교사 과목명은 소문자 set으로 저장하여 자격 검사를 수행합니다. 입력은 지정 형식을 따른다고 가정합니다.

## 4. Task1.py — 기본 시간표 알고리즘

### solution 표현

강의 하나를 다음 세 gene으로 표현합니다.

```python
[start_time, classroom_index, teacher_index]
```

강의가 N개면 solution 길이는 `3 * N`입니다. 각 위치의 강의는 `common.LECTURES` 순서로 정해져 있으므로 모든 강의가 정확히 한 번 표현됩니다. 강의 시간(duration)은 입력에서 가져옵니다.

### 모든 함수

| 함수 | 기능과 반환값 |
|---|---|
| `decode_solution(solution)` | 숫자 배열을 강의명·시작/종료 시간·강의실·교사를 가진 schedule list로 변환 |
| `overlap(first, second)` | 두 강의의 시간 구간이 겹치면 `True` 반환 |
| `evaluate_schedule(schedule)` | 네 종류의 hard constraint 위반 수를 dictionary로 반환 |
| `fitness_function(ga_instance, solution, solution_idx)` | schedule을 평가해 `10000 - 600 × 총 위반 수` 반환 |
| `create_gene_space()` | 각 gene에 허용되는 값들의 list를 생성 |
| `create_ga(**options)` | 기본 설정과 전달된 옵션을 합쳐 `pygad.GA` 객체 반환 |
| `print_schedule(schedule)` | 시작 시간과 강의실 순으로 정렬하여 시간표 출력 |
| `main()` | 데이터 로딩 → GA 실행 → 최종 최상위 후보 평가 → 결과와 시간표 출력 |

### 핵심 코드

`solution[index * 3]`, `solution[index * 3 + 1]`, `solution[index * 3 + 2]`는 해당 강의의 시간, 방, 교사 gene을 읽습니다. 방과 교사 gene은 이름 목록의 index입니다.

```python
{**lecture, "start": start, "end": start + lecture["duration"], ...}
```

`**lecture`는 기존 강의 dictionary 항목을 새 dictionary에 펼칩니다. 그 뒤 배정 정보를 추가합니다.

```python
first["start"] < second["end"] and second["start"] < first["end"]
```

두 구간의 겹침 조건입니다. `<`를 사용하므로 한 강의가 끝나는 시각에 다른 강의가 시작하는 것은 허용됩니다.

`schedule[index + 1:]`는 현재 강의 뒤의 강의만 선택합니다. 자기 자신과 비교하지 않고, A-B와 B-A를 중복 계산하지 않습니다. 방과 교사가 모두 같으면 같은 강의 쌍에서 두 위반을 셉니다.

`range(first_hour, last_hour - duration + 1)`의 끝값은 포함되지 않으므로 `+1`을 붙여 가장 늦게 시작할 수 있는 시각도 포함합니다. 이 범위는 모든 방의 가장 이른 개방과 가장 늦은 종료를 사용합니다. 선택한 개별 방의 운영시간 준수 여부는 fitness가 검사합니다.

```python
def create_ga(**options):
    settings = dict(...)
    settings.update(options)
    return pygad.GA(**settings)
```

함수 정의의 `**options`는 키워드 인자를 dictionary로 모읍니다. `update()`는 지정한 기본값을 덮어씁니다. 호출의 `**settings`는 dictionary를 개별 키워드 인자로 펼칩니다.

기본 설정은 population 300, 최대 800세대, 부모 80개, seed 12, 정수 gene입니다. 기본 설정에 성공 시 자동 종료 조건은 없습니다. 다른 Task는 필요한 설정을 덮어씁니다.

`ga.best_solution(pop_fitness=ga.last_generation_fitness)`는 최종 population의 fitness를 전달해 최상위 후보를 가져옵니다. 반환값은 solution, fitness, index이며 `_`는 사용하지 않는 index를 받습니다. `not any(errors.values())`는 모든 위반 수가 0일 때 `True`입니다.

### 출력 의미

| 출력 | 의미 |
|---|---|
| `Best fitness` | 반환된 최상위 시간표의 점수. 10000이면 위반 0개 |
| `invalid_teacher` | 담당할 수 없는 과목을 배정받은 강의 수 |
| `unavailable_classroom` | 강의실 사용 가능 시간을 벗어난 강의 수 |
| `classroom_overlap` | 같은 방에서 시간대가 겹치는 강의 쌍 수 |
| `teacher_overlap` | 같은 교사가 동시에 맡은 강의 쌍 수 |
| `is_valid` | 위반이 전혀 없으면 True |
| `Start-End / Room / Subject / Teacher` | 강의 시간 구간, 방, 과목, 담당 교사 |

예를 들어 fitness 9400은 위반 1개, -14000은 위반 40개를 뜻합니다. 위반 수가 17개 이상이면 fitness는 음수가 됩니다. 점수는 높을수록 좋습니다.

## 5. Task2.py — custom 연산

| 함수 | 기능과 반환값 |
|---|---|
| `crossover(parents, offspring_size, ga)` | 강의별 gene 세 개를 묶어서 부모 배열을 잘라 붙인 offspring NumPy 배열 반환 |
| `lecture_errors(solution, index)` | 지정 강의의 자격·방 운영시간·다른 강의와의 충돌 위반 합계 반환 |
| `mutation(children, ga)` | offspring마다 gene 하나 변경을 시도하고 위반이 늘지 않으면 적용. 변경된 배열 반환 |
| `run(label, **operators)` | GA 실행, 단계별 시간과 fitness 변화 출력, fitness history 반환 |
| `main()` | 기본 입력을 로딩하고 Custom GA 한 번 실행 |

### crossover

`i % len(parents)`와 `(i + 1) % len(parents)`는 부모 목록 끝에서 다시 처음으로 돌아가며 인접한 두 부모를 선택합니다.

```python
cut = 3 * ga.python_random_generator.randint(1, len(common.LECTURES))
np.concatenate((first[:cut], second[cut:]))
```

절단 위치를 3의 배수로 만들어 강의의 세 gene을 함께 유지합니다. 앞부분은 첫 부모, 뒷부분은 둘째 부모에서 가져옵니다. `randint`는 양끝을 포함하므로 마지막 위치를 고르면 첫 부모가 그대로 복사됩니다. 이 crossover 자체가 충돌이나 교사 자격을 보장하지는 않습니다.

### mutation

`candidate = child.copy()`는 시험용 복사본을 만듭니다. `randrange`로 gene 위치 하나를 선택하고 `choice(ga.gene_space[gene])`로 허용값 하나를 뽑습니다. 기존 값과 같은 값이 선택될 수도 있습니다.

`gene // 3`은 정수 나눗셈으로 해당 gene이 속한 강의 index를 구합니다. 예를 들어 gene 6, 7, 8은 모두 강의 index 2에 속합니다.

```python
if lecture_errors(candidate, lecture_index) <= lecture_errors(child, lecture_index):
    child[gene] = candidate[gene]
```

위반 수가 같거나 줄면 변경을 채택합니다. 하나의 강의만 바뀌므로 나머지 강의끼리의 위반은 동일합니다. 따라서 이 판단은 현재 Task 1 fitness를 전체 재계산해 비교하는 것과 같습니다. 강의 수 N에 대해 각 비교에서 모든 쌍을 검사하는 O(N²) 대신 해당 강의와 나머지를 검사하는 O(N) 작업을 수행합니다. schedule 해석도 O(N)입니다.

`errors += 조건`은 Python에서 `True`가 1, `False`가 0으로 계산되는 성질을 이용합니다. `other_index != index`는 자기 자신과의 충돌 검사를 제외합니다.

### 시간 측정과 출력

`on_parents`, `on_crossover`, `on_mutation` callbacks는 각 단계 완료 시각을 list에 기록합니다. `lambda ga, _: ...`는 짧은 함수이며 `_`는 사용하지 않는 callback 인자입니다. 난수는 GA의 generator를 사용합니다.

`np.subtract(crossed, parents)`는 crossover 완료 시각에서 부모 선택 완료 시각을 뺍니다. mutation도 같은 방식으로 계산합니다. 평균에 1000을 곱해 초를 밀리초로 변환합니다. callbacks 사이의 구간 측정이므로 작은 호출 overhead가 포함됩니다.

| 출력 | 의미 |
|---|---|
| `Task 2 (... s)` | GA 생성과 실행에 걸린 전체 시간 |
| `crossover: ... ms/generation` | 한 세대 offspring 전체 crossover 구간의 평균 시간 |
| `mutation: ... ms/generation` | 한 세대 offspring 전체 mutation 구간의 평균 시간 |
| `Generation g: best fitness f` | g세대 최고 fitness. 최초 기록과 이전 세대에서 값이 달라진 시점만 출력 |

Generation 0은 초기 population 평가입니다. 마지막으로 출력된 세대가 실제 종료 세대와 같을 필요는 없습니다. 이후 fitness 변화가 없으면 추가 줄을 출력하지 않습니다.

## 6. Task3.py — Teacher preferences와 Teacher balance

| 함수 | 기능과 반환값 |
|---|---|
| `read_preferences()` | Preferences.txt를 읽어 교사별 likes/dislikes dictionary 반환 |
| `measure(solution, preferences)` | `(violations, liked, disliked, gap, hours)` 반환 |
| `starting_population()` | Task 2 연산으로 warm-up 실행 후 최종 후보 64개를 가져오고 첫 후보에 warm-up 최상위 해 배치 |
| `result_priority(result)` | 출력할 대표 후보를 선택할 정렬 기준 반환 |
| `run(method, population, preferences)` | 지정한 목적함수·selection 방식으로 GA 실행 후 대표 후보의 측정값 반환 |
| 내부 함수 `fitness(ga, solution, index)` | Weighted sum이면 숫자 하나, NSGA-II이면 두 점수의 list 반환 |
| `compare()` | 같은 초기 집단으로 두 방식을 실행·출력하고 method별 결과 dictionary 반환 |
| `main()` | `compare()` 실행 |

### preferences와 balance 계산

`json.loads("{" + values.replace(...))`는 입력의 곡선 따옴표를 일반 쌍따옴표로 바꾸고 dictionary로 읽습니다.

`dict.fromkeys(common.TEACHERS, 0)`은 모든 교사의 강의시간을 0으로 시작합니다. 배정이 없는 교사도 balance 계산에 포함됩니다.

강의의 각 정수 시간 구간에 대해 likes 범위에 속하면 `liked`, dislikes 범위에 속하면 `disliked`를 1씩 늘립니다. 10~12시 수업이 likes `[10, 11]`과 겹치면 선호 시간은 1시간입니다. 두 조건은 각각 검사합니다.

```python
gap = max(hours.values()) - min(hours.values())
```

가장 많이 가르치는 교사와 가장 적게 가르치는 교사의 시간 차이입니다. 작을수록 균형이 좋습니다.

### 두 최적화 방식

```python
preference = liked - disliked
penalty = (3 * total_hours + 1) * violations

# Weighted sum
return preference - gap - penalty

# NSGA-II
return [preference - penalty, -gap - penalty]
```

Weighted sum은 preference와 balance를 하나의 점수로 합치고 `sss` selection을 사용합니다. NSGA-II는 두 목표를 따로 유지하고 `nsga2` selection을 사용합니다. NSGA-II는 Non-dominated Sorting Genetic Algorithm II의 약자입니다. 한 목표에서 더 좋고 다른 목표에서 더 나쁜 후보들을 함께 고려합니다.

총 강의시간을 H라고 하면 preference는 -H~H, gap은 0~H입니다. 따라서 `3*H+1`의 penalty는 hard violation 하나가 soft score의 이득으로 상쇄되지 않게 합니다. Task 3의 fitness는 Task 1의 10000점 기준과 다릅니다.

두 실행은 같은 64개 초기 후보의 `.copy()`를 전달받고 80세대, 부모 16개, seed 12로 실행합니다. 본 실행의 crossover/mutation은 PyGAD 기본값을 사용합니다. Task 2의 custom 연산은 warm-up에서 사용합니다.

```python
return -violations, liked - disliked - gap, -gap
```

`max(rows, key=result_priority)`는 이 tuple을 왼쪽부터 비교합니다. 위반 수가 적은 후보를 우선하고, 같으면 preference-gap이 큰 후보, 다시 같으면 gap이 작은 후보를 고릅니다. NSGA-II에서도 이 규칙으로 대표 하나를 출력하므로 Pareto front 전체를 출력하는 것은 아닙니다.

### 출력 의미

| 출력 | 의미 |
|---|---|
| `Weighted sum`, `NSGA-II` | 실행한 최적화 방식 |
| `violations` | hard constraint 위반 수 |
| `liked` | 선호 시간에 배정된 총 강의시간 |
| `disliked` | 비선호 시간에 배정된 총 강의시간 |
| `gap` | 교사별 최대 강의시간과 최소 강의시간의 차이 |
| `Teaching hours` | 교사별 총 배정 강의시간 dictionary |

예를 들어 `liked=10 h, disliked=4 h, gap=3 h`이면 preference는 6이고, hard violation이 없을 때 Weighted sum 점수는 3입니다. 두 방식이 같은 대표 결과를 출력해도 알고리즘 전체의 동작이 같다는 뜻은 아닙니다.

## 7. Task4.py — 실험과 측정

| 함수 | 기능과 반환값 |
|---|---|
| `run_case(case, method, population)` | 이미 로딩된 데이터로 GA 한 번 실행 후 측정 결과 dictionary 반환 |
| 내부 함수 `record_fitness(ga, fitness)` | fitness 평가 callback에서 최초 유효 해의 세대와 시간을 한 번 기록 |
| `experiment()` | 네 입력과 세 설정의 12개 실행 결과 출력, 결과 dictionary들의 list 반환 |
| `main()` | `experiment()` 실행 |

각 입력에서 Default/60, Custom/60, Custom/120을 실행합니다. 앞의 두 실행은 연산자 차이를, 뒤의 두 Custom 실행은 population 크기 차이를 비교합니다. 모든 실행은 부모 16개, seed 12, 100세대를 사용합니다.

### 어려운 코드

`nonlocal first_valid, time_to_valid`는 내부 callback이 바깥 `run_case()`의 변수를 갱신하도록 합니다.

```python
if first_valid is None and max(fitness) >= 10_000:
```

처음 유효한 해가 관측되었을 때만 기록합니다. 이후 성공 상태가 반복되어도 값을 덮어쓰지 않습니다. 초기 population이 이미 유효하면 세대 0이 기록될 수 있습니다. 시간은 GA 생성 직전부터 해당 population의 평가 callback까지 측정하므로 준비 시간과 평가 시간이 포함됩니다.

`stop_criteria=None`으로 100세대를 끝까지 실행합니다. 이 때문에 최초 성공 시간과 전체 실행 시간을 별도로 저장합니다.

`zip(parents, crossed)`는 두 단계의 시각을 같은 세대끼리 묶습니다. `mean(end - start for ...)`는 각 구간 길이의 평균을 계산합니다.

`try ... finally`는 실험 도중 오류가 발생하더라도 루트의 기본 데이터를 다시 로딩합니다. 파일 내용은 변경하지 않습니다.

### 출력 열과 반환 dictionary

| 출력 열 | dictionary key | 의미 |
|---|---|---|
| Input | `case` | 입력 집단 |
| Method | `method` | Default 또는 Custom |
| Pop | `population` | 세대당 시간표 후보 수 |
| First gen | `first_valid` | 최초 유효 해의 세대. 실패하면 None |
| Time to valid(s) | `time_to_valid` | 최초 성공 관측까지 걸린 초. 실패하면 None이며 표에는 Not found |
| Total(s) | `total_time` | 준비와 100세대 전체 실행 시간 |
| Cross(ms/gen) | `crossover_ms` | 세대당 평균 crossover 구간 시간 |
| Mutation(ms/gen) | `mutation_ms` | 세대당 평균 mutation 구간 시간 |
| Best | `best` | 마지막 기록의 최고 fitness |
| 그래프 데이터 | `history` | 초기 상태부터 세대별 최고 fitness의 list |

성공 시간을 비교할 때 실패한 실행의 Total을 성공 시간으로 해석하면 안 됩니다. Task 4는 seed 하나의 결과를 보여주며, 시간은 실행 환경과 부하에 따라 달라집니다. Large/Difficult에서 실패하는 것은 해당 예산에서 유효한 시간표를 찾지 못했다는 의미입니다.

## 8. Task4.ipynb — 결과와 그래프

처음 네 셀은 Task 1, Task 2, Task 3, Task 4를 실행합니다. 마지막 셀은 `runs`에서 그래프용 데이터를 구성합니다.

현재 Task 4는 dictionary list를 반환합니다. 예전 버전은 `(case, method, population, first_valid, elapsed, history)` tuple list를 반환했습니다. `isinstance(row, dict)`는 형식을 확인하고, tuple이면 필요한 항목을 dictionary로 옮깁니다. 이 처리로 기존 커널의 tuple 데이터도 그래프에 사용할 수 있습니다.

```python
cases = list(dict.fromkeys(row["case"] for row in plot_rows))
```

각 결과의 case를 꺼내 generator로 전달하고 dictionary key의 중복 제거를 이용합니다. 이후 list로 바꾸면 처음 나타난 순서를 유지한 네 입력 이름을 얻습니다.

`plt.subplots(2, 2, ..., sharex=True)`는 가로축을 공유하는 네 그래프를 만듭니다. `axes.flat`은 2차원 axes 배열을 순서대로 순회하게 해 주며, `zip(cases, axes.flat)`은 각 입력을 그래프 하나에 연결합니다.

`ax.step(..., where="post")`는 해당 세대의 값을 다음 세대까지 유지하는 계단 그래프를 그립니다. `fig.tight_layout()`은 제목과 축 레이블이 겹치지 않도록 여백을 조절합니다.

| 그래프 요소 | 의미 |
|---|---|
| 제목 | Small/Large와 Easy/Difficult 입력 조합 |
| Generation | 세대 번호. 0은 초기 population |
| Best fitness | 해당 세대 최고 fitness. 위로 갈수록 좋음 |
| Default / 60 등 | 연산자 방식과 population 크기 |
| 10000에 도달 | hard constraint 위반 0개인 후보 발견 |

가로축은 공유하지만 세로축은 그래프마다 자동 설정됩니다. 서로 다른 패널의 선 높이보다 실제 숫자를 비교해야 합니다.

Python은 import한 모듈을 커널에 보관합니다. `.py` 수정 후 결과가 이전과 같거나 형식 오류가 나면 kernel을 재시작한 뒤 전체 셀을 순서대로 실행합니다. 저장된 output은 마지막 실행 당시 결과이며 코드를 수정했다고 자동 갱신되지는 않습니다.

## 9. 공통 문법과 해석 시 주의점

| 표현 | 의미 |
|---|---|
| `if __name__ == "__main__":` | 파일을 직접 실행할 때만 아래 main 함수 호출 |
| `**operators` | dictionary의 항목을 키워드 인자로 전달 |
| `.copy()` | 시험 변경이나 별도 실행이 원본 배열에 영향을 주지 않도록 복사 |
| `lambda` | 짧은 익명 함수. 정렬 기준과 callback에서 사용 |
| `f"{value:.3f}"` | 숫자를 소수점 세 자리로 표시 |
| `f"{value:>9}"` | 폭 9칸으로 오른쪽 정렬 |
| `None` | 아직 값이 없거나 해당 실행에서 성공하지 못한 상태 |

Task 1·2의 기본 탐색은 800세대이며 최초 성공 시 자동으로 끝나지 않습니다. Task 3은 warm-up 이후 별도의 80세대 비교를 수행합니다. Task 4는 100세대 제한으로 새 실험을 수행하므로 Task 2 단독 실행과 성공 세대가 달라도 모순이 아닙니다.

현재 `lecture_errors()`는 Task 1의 제약 검사와 같은 규칙을 사용합니다. 새 제약을 추가할 때는 mutation의 부분 검사에도 영향을 검토해야 합니다. 또한 Task 2 mutation은 hard constraint fitness에 맞춘 방식이므로 Task 3의 soft objectives에 그대로 적용하면 별도 검토가 필요합니다.
