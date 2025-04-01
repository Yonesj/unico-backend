from django.db import transaction
from src.courses.models import Exam


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
