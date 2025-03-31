from django.db import transaction
from .models import Course, ClassSession, Exam


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
    'course_map' is a dict mapping course.id to Course instance.
    """
    all_sessions = []

    for data in cleaned_courses:
        course = course_map.get(data["id"])
        if not course:
            continue

        for session in data.get("classes", []):
            all_sessions.append(ClassSession(
                course=course,
                day=session["day"],
                start=session["start"],
                end=session["end"],
                is_problem_solving=session["is_problem_solving"]
            ))
    # Delete existing ClassSession records for all affected courses in one query.
    course_ids = [course.id for course in course_map.values()]
    ClassSession.objects.filter(course_id__in=course_ids).delete()

    if all_sessions:
        ClassSession.objects.bulk_create(all_sessions)


def bulk_save_exams(cleaned_courses, course_map):
    """
    Bulk update or create Exam records efficiently.
    Each cleaned course dict may contain an "exam" key with exam data.
    For courses with no exam data, any existing exam is deleted.
    """
    exam_data_list = []
    exam_course_ids = []

    for data in cleaned_courses:
        exam = data.get("exam")
        if exam:
            course_id = data["id"]
            exam_data_list.append((course_id, exam))
            exam_course_ids.append(course_id)

    existing_exams = Exam.objects.filter(course_id__in=exam_course_ids)
    existing_exam_map = {exam.course_id: exam for exam in existing_exams}

    exams_to_update = []
    exams_to_create = []

    for course_id, exam_data in exam_data_list:
        if course_id in existing_exam_map:
            exam_obj = existing_exam_map[course_id]
            exam_obj.date = exam_data["date"]
            exam_obj.start = exam_data["start"]
            exam_obj.end = exam_data["end"]
            exams_to_update.append(exam_obj)
        else:
            course = course_map.get(course_id)
            if course:
                exam_obj = Exam(
                    course=course,
                    date=exam_data["date"],
                    start=exam_data["start"],
                    end=exam_data["end"]
                )
                exams_to_create.append(exam_obj)

    with transaction.atomic():
        if exams_to_create:
            Exam.objects.bulk_create(exams_to_create)
        if exams_to_update:
            Exam.objects.bulk_update(exams_to_update, ["date", "start", "end"])

        all_course_ids = [course.id for course in course_map.values()]
        courses_with_exam = set(exam_course_ids)
        Exam.objects.filter(course_id__in=[cid for cid in all_course_ids if cid not in courses_with_exam]).delete()
