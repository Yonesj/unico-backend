from rest_framework.pagination import PageNumberPagination


class TenPerPagePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = None
    max_page_size = 10
