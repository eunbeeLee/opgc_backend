from rest_framework.pagination import CursorPagination


class IdOrderingPagination(CursorPagination):
    page_size = 10
    max_page_size = 1000
    ordering = 'id'
