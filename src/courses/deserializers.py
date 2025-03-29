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
    cleaned_list = []

    if not prerequisites:
        cleaned_list.append("مقدار پیش‌فرض")

    for item in prerequisites:
        item = item.strip()
        item = item.replace("\n", " ").strip()
        if item:
            cleaned_list.append(item)

    if not cleaned_list:
        cleaned_list.append("مقدار پیش‌فرض")

    return cleaned_list


"""Extracts class days, times, and exam date/time from the provided string."""

def time_decomposition(time_str):
    try:
        start, end = map(str.strip, time_str.split('-'))

        start_hour = start.split(':')[0]
        end_hour = end.split(':')[0]

        return {"start": start_hour, "end": end_hour}
    except ValueError:
        return {"start": -1, "end": -1}


def determine_day(s):
    days = {
        'ش': WeekDay.SATURDAY,
        'ي': WeekDay.SUNDAY,
        'د': WeekDay.MONDAY,
        'س': WeekDay.TUESDAY,
        'چ': WeekDay.WEDNESDAY,
        'پ': WeekDay.THURSDAY,
        'ج': WeekDay.FRIDAY
    }
    day = days.get(s[0], WeekDay.NONE)
    return day[1] if day != WeekDay.NONE else -1


def determine_exam_day(s):
    days = {
        '1': WeekDay.SATURDAY,
        '2': WeekDay.SUNDAY,
        '3': WeekDay.MONDAY,
        '4': WeekDay.TUESDAY,
        '5': WeekDay.WEDNESDAY,
        '6': WeekDay.THURSDAY,
        '7': WeekDay.FRIDAY
    }
    day = days.get(s, WeekDay.NONE)
    return day[1] if day != WeekDay.NONE else -1


def extract_class_exam_info(class_day):
    arr = class_day.strip().split("\n")
    class_sessions = []
    exam_info = None

    for item in arr:
        if not item:
            continue

        if item.startswith("ا"):
            match = re.search(r'امتحان\((\d{4})\.(\d{2})\.(\d{2})\)', item)
            if match:
                date = f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
                j_date = jdatetime.datetime.strptime(date, "%Y/%m/%d").date()
                day_of_week = (j_date.weekday() + 1) % 7
            else:
                date, day_of_week = "0", -1

            times = time_decomposition(item[-11:])
            exam_info = {
                "date": date,
                "day": determine_exam_day(str(day_of_week)),
                "start": times["start"],
                "end": times["end"]
            }
            continue

        record = {"isExerciseSolving": True}
        temp = item.split("): ")[-1]
        index = temp.find('-')

        if index == -1:
            continue

        times = time_decomposition(temp[index - 5:index + 6])
        record["day"] = determine_day(temp)
        record["start"] = times["start"]
        record["end"] = times["end"]
        if item[0] == 'د':
            record['isExerciseSolving'] = False
        if 'مکان: ' in temp:
            record['location'] = temp.split('مکان: ').pop()

        class_sessions.append(record)

    return class_sessions, exam_info


class CourseRawDataDeserializer(serializers.Serializer):
    course_code = serializers.CharField()
    course_name = serializers.CharField()
    theory = serializers.CharField()
    practical = serializers.CharField()
    capacity = serializers.CharField()
    gender = serializers.CharField()
    professor_name = serializers.CharField()
    classes = serializers.CharField(allow_blank=True)
    class_location = serializers.CharField(allow_blank=True)
    prerequisites = serializers.CharField(allow_blank=True, required=False)
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
        return parse_prerequisites(value)

    def clean_class_day(self, value):
        """
        Process the 'class_day' field into:
          - A list of class sessions
          - Exam information as a dict (or None if absent)
        """
        return extract_class_exam_info(value)

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
        ret["prerequisites"] = self.clean_prerequisites(ret.get("prerequisites", []))
        ret["notes"] = self.clean_string_value(ret["notes"])

        # Extract class sessions and exam info
        classes, exam_info = self.clean_class_day(ret["classes"])
        ret["classes"] = classes
        ret["exam_info"] = exam_info

        return ret

    def create(self, validated_data):
        """
        If the course exists (by course_code) update it, else create it.
        Also update or create the related ClassSession and Exam objects.
        """
        # Extract nested values
        classes = validated_data.pop("classes")
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
                "professor_name": validated_data["professor_name"],
                "class_location": validated_data["class_location"],
                "prerequisites": validated_data["prerequisites"],
                "notes": validated_data["notes"],
            }
        )

        # Clear previous class sessions and re-create them.
        course.classes.all().delete()
        for session in classes:
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
