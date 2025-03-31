import re
from src.courses.models import Gender, WeekDay


def determine_gender(s):
    """ Determines gender based on the input string """
    GENDER_MAPPING = {
        "مختلط": Gender.BOTH,
        "مرد": Gender.MALE,
        "زن": Gender.FEMALE,
    }
    return GENDER_MAPPING.get(s.strip(), Gender.BOTH)


def time_decomposition(time_str):
    """ Use regex to extract hours from a time range like "10:00-12:00" or "8:00-10:00"""
    match = re.search(r'(\d{1,2}):\d{2}\s*-\s*(\d{1,2}):\d{2}', time_str)
    if match:
        return {"start": int(match.group(1)), "end": int(match.group(2))}
    return {"start": -1, "end": -1}


def determine_day(s: str):
    """ Remove leading/trailing spaces, then take the first character to determine day """
    DAY_MAPPING = {
        'ش': WeekDay.SATURDAY,
        'ي': WeekDay.SUNDAY,
        'د': WeekDay.MONDAY,
        'س': WeekDay.TUESDAY,
        'چ': WeekDay.WEDNESDAY,
        'پ': WeekDay.THURSDAY,
        'ج': WeekDay.FRIDAY
    }
    return DAY_MAPPING.get(s.strip()[0], WeekDay.NONE)


def extract_class_sessions_and_exam_info(class_day):
    """
    Extracts class sessions and exam info from the given multiline string.
    Returns a tuple: (list of class sessions, exam_info dictionary or None)
    """
    arr = class_day.strip().split("\n")
    class_sessions = []
    exam_info = None

    for item in arr:
        item = item.strip()
        if not item:
            continue

        if item.startswith("امتحان"):
            match = re.search(r'امتحان\((\d{4})\.(\d{2})\.(\d{2})\)', item)
            date = f"{match.group(1)}/{match.group(2)}/{match.group(3)}" if match else "0"
            times = time_decomposition(item)

            exam_info = {
                "date": date,
                "start": times["start"],
                "end": times["end"]
            }

        else:
            record = {"isExerciseSolving": True}
            # Example: "درس(ت): سه شنبه 10:00-12:00"
            parts = item.split("): ")

            if len(parts) < 2:
                continue

            temp = parts[-1]
            times = time_decomposition(temp)
            record["start"] = times["start"]
            record["end"] = times["end"]
            record["day"] = determine_day(temp)

            if item.startswith("درس"):
                record["isExerciseSolving"] = False

            class_sessions.append(record)

    return class_sessions, exam_info
