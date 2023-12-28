from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    def get_page_size(self, request):
        if 'page_size' in request.query_params:
            return request.query_params.get('page_size')
        return self.page_size