from src.courses.models import ClassSession


def bulk_save_class_sessions(course_map, cleaned_courses):
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

    course_ids = [course.id for course in course_map.values()]
    ClassSession.objects.filter(course_id__in=course_ids).delete()

    if all_sessions:
        ClassSession.objects.bulk_create(all_sessions)
