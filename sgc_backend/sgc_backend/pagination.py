from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    def __init__(self, page_size_query_param='page_size'):
        self.page_size_query_param = page_size_query_param

    def get_page_size(self, request):
        if self.page_size_query_param in request.query_params:
            return request.query_params.get(self.page_size_query_param)
        return self.page_size
