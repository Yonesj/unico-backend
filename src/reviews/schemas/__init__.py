from .faculty_schema import faculty_list_view_schema
from .professor_schema import (
    professor_list_view_schema,
    most_viewed_professors_schema,
    most_popular_professors_schema,
    professor_retrieve_view_schema,
    professor_card_retrieve_schema,
    professor_compare_view_schema
)
from .course_schema import course_list_view_schema
from .professor_proposal_schema import professor_proposal_create_schema
from .professor_revision_schema import professor_revision_create_schema
from .student_schema import student_create_view_schema
from .review_schema import (
    latest_review_list_schema,
    professor_reviews_list_schema,
    my_review_list_schema,
    review_create_schema,
    review_retrieve_schema
)
from .review_report_schema import review_report_create_schema
from .review_revision_schema import review_revision_create_schema
from .review_reaction_schema import (
    review_reaction_create_schema, review_reaction_update_destroy_schema, my_review_reaction_list_schema
)
