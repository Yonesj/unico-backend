from .helper_functions import determine_gender, extract_class_sessions_and_exam_info


class CrawlerRawDataCleaner:

    @staticmethod
    def clean_string_value(value):
        return value.strip() if isinstance(value, str) else value

    @staticmethod
    def clean_numeric_value(value):
        try:
            return int(value.strip())
        except (ValueError, AttributeError):
            return 0

    @staticmethod
    def clean_gender(value):
        return determine_gender(value)

    @staticmethod
    def clean_prerequisites(value):
        """
        Join the list of prerequisites into a single string.
        """
        if isinstance(value, list):
            return ": ".join(item.strip() for item in value if item.strip())
        return ""

    @staticmethod
    def clean_classes(value):
        """
        Process the raw 'classes' field (a multiline string) into two parts:
          - A list of class sessions (each is a dict with day, start, end, etc.)
          - Exam information as a dict (or None if absent)
        """
        return extract_class_sessions_and_exam_info(value)

    def clean(self, data):
        """
        Clean each field from the raw data and return a dictionary with the cleaned data.
        """
        cleaned = {
            "course_code": self.clean_string_value(data.get("course_code", "")),
            "course_name": self.clean_string_value(data.get("course_name", "")),
            "theory": self.clean_string_value(data.get("theory", "")),
            "practical": self.clean_string_value(data.get("practical", "")),
            "capacity": self.clean_numeric_value(data.get("capacity", "0")),
            "gender": self.clean_gender(data.get("gender", "")),
            "professor_name": self.clean_string_value(data.get("professor_name", "")),
            "class_location": self.clean_string_value(data.get("class_location", "")),
            "prerequisites": self.clean_prerequisites(data.get("prerequisites", [])),
            "notes": self.clean_string_value(data.get("notes", ""))
        }

        cleaned["id"] = self.clean_numeric_value(cleaned["course_code"].replace("_", ""))
        cleaned["classes"], cleaned["exam"] = self.clean_classes(data.get("classes", ""))

        return cleaned
