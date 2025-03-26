class StudentCoursesData:
    def __init__(self, student_id, full_name, course_code, course_name, theory, practical, capacity, gender,
                 professor_name, class_day, class_location, prerequisites, notes):
        self.student_id = student_id
        self.full_name = full_name
        self.course_code = course_code
        self.course_name = course_name
        self.theory = theory
        self.practical = practical
        self.capacity = capacity
        self.gender = gender
        self.professor_name = professor_name
        self.class_day = class_day
        self.class_location = class_location
        self.prerequisites = prerequisites
        self.notes = notes

    def __repr__(self):
        return f"StudentCourseData({self.student_id}, {self.full_name}, {self.course_code}, {self.course_name}, {self.gender}, {self.professor_name}, {self.exam_schedule}, {self.model}, {self.pre_requisites}, {self.notes})"

    def to_dict(self):
        return self.__dict__