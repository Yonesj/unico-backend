import re
from rest_framework import serializers
from .models import Course, ClassSession, Exam, Gender, WeekDay

import jdatetime


def determine_gender(s):
    """ Determines gender based on the input string """
    GENDER_MAPPING = {
        "مختلط": Gender.BOTH,
        "مرد": Gender.MALE,
        "زن": Gender.FEMALE,
    }
    return GENDER_MAPPING.get(s, Gender.BOTH)


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


DAY_MAPPING = {
    "شنبه": WeekDay.SATURDAY,
    "يك شنبه": WeekDay.SUNDAY,
    "دوشنبه": WeekDay.MONDAY,
    "سه شنبه": WeekDay.TUESDAY,
    "چهارشنبه": WeekDay.WEDNESDAY,
    "پنج شنبه": WeekDay.THURSDAY,
    "جمعه": WeekDay.FRIDAY,
}

class CourseRawDataDeserializer(serializers.Serializer):
    course_code = serializers.CharField()
    course_name = serializers.CharField()
    theory = serializers.CharField()
    practical = serializers.CharField()
    capacity = serializers.CharField()
    gender = serializers.CharField()
    professor_name = serializers.CharField()
    class_day = serializers.CharField(allow_blank=True)
    class_location = serializers.CharField(allow_blank=True)
    prerequisites = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    notes = serializers.CharField(allow_blank=True)

    def clean_string_value(self, value):
        return value.strip()

    def clean_numeric_value(self, value):
        try:
            return int(value.strip())
        except ValueError:
            return 0  # Handle cases where value is missing or invalid

    def clean_gender(self, value):
        return determine_gender(value.strip())

    def clean_prerequisites(self, value):
        return [item.strip() for item in value if item.strip()]

    def clean_class_day(self, value):
        """
        Process the 'class_day' field into:
          - A list of class sessions
          - Exam information as a dict (or None if absent)
        """
        class_sessions = []
        exam_info = None

        for line in value.splitlines():
            line = line.strip()
            if not line:
                continue

            # Parse class session
            match = re.search(r"درس\(ت\):\s*(\S+)\s+(\d{1,2}):\d{2}-(\d{1,2}):\d{2}", line)
            if match:
                day_raw = match.group(1)
                start_hour = int(match.group(2))
                end_hour = int(match.group(3))
                day = DAY_MAPPING.get(day_raw, WeekDay.NONE)

                class_sessions.append({
                    "day": day,
                    "start": start_hour,
                    "end": end_hour
                })

            # Parse exam info
            match = re.search(r"امتحان\(([\d\.]+)\).*?(\d{1,2}):\d{2}-(\d{1,2}):\d{2}", line)
            if match:
                exam_info = {
                    "date": match.group(1),
                    "start": int(match.group(2)),
                    "end": int(match.group(3))
                }

        return class_sessions, exam_info

    def to_internal_value(self, data):
        """
        Override to_internal_value to clean each field before validation.
        """
        ret = super().to_internal_value(data)
        ret["course_code"] = self.clean_string_value(ret["course_code"])
        ret["course_name"] = self.clean_string_value(ret["course_name"])
        ret["theory"] = self.clean_numeric_value(ret["theory"])
        ret["practical"] = self.clean_numeric_value(ret["practical"])
        ret["capacity"] = self.clean_numeric_value(ret["capacity"])
        ret["gender"] = self.clean_gender(ret["gender"])
        ret["professor_name"] = self.clean_string_value(ret["professor_name"])
        ret["class_location"] = self.clean_string_value(ret["class_location"])
        ret["prerequisites"] = self.clean_prerequisites(ret["prerequisites"])
        ret["notes"] = self.clean_string_value(ret["notes"])

        # Extract class sessions and exam info
        class_sessions, exam_info = self.clean_class_day(ret["class_day"])
        ret["class_sessions"] = class_sessions
        ret["exam_info"] = exam_info

        return ret

    def create(self, validated_data):
        """
        If the course exists (by course_code) update it, else create it.
        Also update or create the related ClassSession and Exam objects.
        """
        # Extract nested values
        class_sessions = validated_data.pop("class_sessions")
        exam_info = validated_data.pop("exam_info")

        # Use update_or_create: note that .save() on the model uses the course_code to generate id.
        course, created = Course.objects.update_or_create(
            course_code=validated_data["course_code"],
            defaults={
                "course_name": validated_data["course_name"],
                "theory": validated_data["theory"],
                "practical": validated_data["practical"],
                "capacity": validated_data["capacity"],
                "gender": validated_data["gender"],
                "professor_name": validated_data["professor"],
                "class_location": validated_data["class_location"],
                "prerequisites": validated_data["prerequisites"],
                "notes": validated_data["notes"],
            }
        )

        # Clear previous class sessions and re-create them.
        course.classes.all().delete()
        for session in class_sessions:
            ClassSession.objects.create(
                course=course,
                day=session["day"],
                start=session["start"],
                end=session["end"]
            )

        # Update exam info: update_or_create if exam_info exists, otherwise delete any existing exam.
        if exam_info:
            Exam.objects.update_or_create(
                course=course,
                defaults={
                    "date": exam_info["date"],
                    "start": exam_info["start"],
                    "end": exam_info["end"],
                }
            )
        else:
            Exam.objects.filter(course=course).delete()

        return course

    def update(self, instance, validated_data):
        """
        For DRF, if an instance is provided, update it.
        Here we use similar logic to create() but update the given instance.
        """
        # Extract nested values.
        class_sessions = validated_data.pop("class_sessions", [])
        exam_info = validated_data.pop("exam_info", None)

        # Update course fields.
        instance.course_name = validated_data.get("course_name", instance.course_name)
        instance.theory = validated_data.get("theory", instance.theory)
        instance.practical = validated_data.get("practical", instance.practical)
        instance.capacity = validated_data.get("capacity", instance.capacity)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.professor_name = validated_data.get("professor", instance.professor_name)
        instance.class_location = validated_data.get("class_location", instance.class_location)
        instance.prerequisites = validated_data.get("prerequisites", instance.prerequisites)
        instance.notes = validated_data.get("notes", instance.notes)
        instance.save()

        # Update nested relations.
        instance.classes.all().delete()
        for session in class_sessions:
            ClassSession.objects.create(
                course=instance,
                day=session["day"],
                start=session["start"],
                end=session["end"]
            )

        if exam_info:
            Exam.objects.update_or_create(
                course=instance,
                defaults={
                    "date": exam_info["date"],
                    "start": exam_info["start"],
                    "end": exam_info["end"],
                }
            )
        else:
            Exam.objects.filter(course=instance).delete()

        return instance
