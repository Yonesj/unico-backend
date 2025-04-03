from django.db import transaction
from src.courses.models import Course


def bulk_save_courses(cleaned_courses):
    """
    Bulk update or create courses efficiently.
    Assumes each cleaned course dict has an "id" key.
    """
    course_ids = [data["id"] for data in cleaned_courses]
    existing_courses = Course.objects.filter(id__in=course_ids)
    existing_courses_map = {course.id: course for course in existing_courses}

    courses_to_create = []
    courses_to_update = []
    valid_fields = ["id", "course_code", "course_name", "theory", "practical", "capacity", "gender", "professor_name",
                    "class_location", "prerequisites", "notes", ]

    for data in cleaned_courses:
        course_id = data["id"]
        course_data = {k: v for k, v in data.items() if k in valid_fields}

        if course_id in existing_courses_map:
            course = existing_courses_map[course_id]
            course.course_name = course_data["course_name"]
            course.theory = course_data["theory"]
            course.practical = course_data["practical"]
            course.capacity = course_data["capacity"]
            course.gender = course_data["gender"]
            course.professor_name = course_data["professor_name"]
            course.class_location = course_data["class_location"]
            course.prerequisites = course_data["prerequisites"]
            course.notes = course_data["notes"]
            courses_to_update.append(course)
        else:
            courses_to_create.append(Course(**course_data))

    with transaction.atomic():
        if courses_to_create:
            Course.objects.bulk_create(courses_to_create)
        if courses_to_update:
            Course.objects.bulk_update(
                courses_to_update,
                [
                    "course_name", "theory", "practical", "capacity",
                    "gender", "professor_name", "class_location", "prerequisites", "notes"
                ]
            )

    return Course.objects.filter(id__in=course_ids)
