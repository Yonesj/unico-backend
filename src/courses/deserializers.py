import re
import jdatetime

""" Determines gender based on the input string """


def determine_gender(s):
    genders = {
        'مختلط': 'both',
        'مرد': 'boy',
        'زن': 'girl'
    }
    return genders.get(s, 'null')


"""Determines prerequisites and co-requisites by parsing the input list."""


def parse_prerequisites(prerequisites):
    pre_needs = []
    co_needs = []

    temp = None
    for item in prerequisites:
        item = item.strip()

        if item.startswith("پيش نياز"):
            temp = pre_needs
        elif item.startswith("هم نياز"):
            temp = co_needs
        elif item.startswith("معادل"):
            temp = None  # حذف موارد معادل
        elif temp is not None:
            item = item.replace("\nمعادل", "").strip()
            if "\nهم نياز" in item:
                course, _ = item.split("\nهم نياز", 1)
                course = course.strip()
                pre_needs.append(course)
                co_needs.append(course)
            else:
                temp.append(item)

    return {"pre_needs": pre_needs, "co_needs": co_needs}


"""Extracts class days, times, and exam date/time from the provided string."""


def time_decomposition(time_str):
    try:
        start, end = map(str.strip, time_str.split('-'))
        return {"start": start, "end": end}
    except ValueError:
        return {"start": -1, "end": -1}


def determine_day(s):
    days = {
        'ش': 0,
        'ي': 1,
        'د': 2,
        'س': 3,
        'چ': 4,
        'پ': 5
    }
    return days.get(s[0], -1)


def times_division(class_day):
    arr = class_day.strip().split("\n")
    result = {
        "times": [],
        "exam_date": {"day": -1, "date": "0", "start": -1, "end": -1}
    }

    for item in arr:
        if not item:
            continue

        if item[0] == 'ا':
            match = re.search(r'امتحان\((\d{4})\.(\d{2})\.(\d{2})\)', item)
            if match:
                date = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
                j_date = jdatetime.datetime.strptime(date, "%Y/%m/%d").date()
                day_of_week = (j_date.weekday() + 1) % 7
            else:
                date, day_of_week = "0", -1

            times = time_decomposition(item[-11:])
            result["exam_date"] = {
                "start": times["start"],
                "end": times["end"],
                "date": date,
                "day": day_of_week
            }
            continue

        record = {"isExerciseSolving": True}
        temp = item.split("): ")[-1]
        print(temp + "\n")
        index = temp.find('-')

        if index == -1:
            continue

        times = time_decomposition(temp[index - 5:index + 6])
        record["day"] = determine_day(temp)
        record["start"] = times["start"]
        record["end"] = times["end"]
        result["times"].append(record)

    return result
