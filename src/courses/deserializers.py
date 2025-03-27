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
