from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
LECTURES = []
CLASSROOMS = {}
TEACHERS = {}


def read_list_file(filename, folder=BASE_DIR):
    """Read lines written as: Name [value, value]."""
    result = {}
    with open(folder / filename, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            name, values = line.split("[", 1)
            result[name.strip()] = [
                value.strip() for value in values.rstrip("]").split(",")
            ]
    return result


def load_data(folder=BASE_DIR):
    """Load the three assignment input files."""
    global LECTURES, CLASSROOMS, TEACHERS
    classes = read_list_file("Classes.txt", folder)
    classroom_data = read_list_file("Classrooms.txt", folder)
    teacher_data = read_list_file("Teachers.txt", folder)

    lectures = []
    for subject, durations in classes.items():
        for number, duration in enumerate(durations, start=1):
            lectures.append(
                {
                    "id": f"{subject}-{number}",
                    "subject": subject,
                    "duration": int(duration),
                }
            )

    classrooms = {
        name: (int(hours[0]), int(hours[1]))
        for name, hours in classroom_data.items()
    }
    teachers = {
        name: {subject.lower() for subject in subjects}
        for name, subjects in teacher_data.items()
    }
    LECTURES, CLASSROOMS, TEACHERS = lectures, classrooms, teachers
