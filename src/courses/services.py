from django.db import transaction
from .models import Course, ClassSession, Exam


def bulk_save_courses(cleaned_courses):
    """
    Bulk update or create courses efficiently.
    """
    course_ids = [data["id"] for data in cleaned_courses]
    existing_courses = Course.objects.filter(id__in=course_ids)
    existing_courses_map = {course.id: course for course in existing_courses}

    courses_to_create = []
    courses_to_update = []

    for data in cleaned_courses:
        course_id = data["id"]
        if course_id in existing_courses_map:
            # Update the existing course.
            course = existing_courses_map[course_id]
            course.course_name = data["course_name"]
            course.theory = data["theory"]
            course.practical = data["practical"]
            course.capacity = data["capacity"]
            course.gender = data["gender"]
            course.professor_name = data["professor_name"]
            course.class_location = data["class_location"]
            course.prerequisites = data["prerequisites"]
            course.notes = data["notes"]
            courses_to_update.append(course)
        else:
            # Create a new course using the provided id.
            courses_to_create.append(Course(**data))

    # Bulk create/update within a transaction.
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


def bulk_update_class_sessions(course_map, cleaned_courses):
    """
    Efficiently update ClassSession records.
    """
    all_sessions = []

    for data in cleaned_courses:
        course = course_map.get(data["id"])
        if course is None:
            continue

        for session in data.get("class_sessions", []):
            all_sessions.append(ClassSession(
                course=course,
                day=session["day"],
                start=session["start"],
                end=session["end"]
            ))
    # Delete existing ClassSession records for all affected courses in one query.
    course_ids = [course.id for course in course_map.values()]
    ClassSession.objects.filter(course_id__in=course_ids).delete()

    if all_sessions:
        ClassSession.objects.bulk_create(all_sessions)