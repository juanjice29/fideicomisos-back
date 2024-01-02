from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        if self.page_size_query_param in request.query_params:
            return request.query_params.get(self.page_size_query_param)
        return self.page_size
    
class EncargoPagination(PageNumberPagination):
    page_size_query_param = 'page_size_encargo'

    def get_page_size(self, request):
        if self.page_size_query_param in request.query_params:
            return request.query_params.get(self.page_size_query_param)
        return self.page_size

class ActorDeContratoPagination(PageNumberPagination):
    page_size_query_param = 'page_size_actores_de_contrato'

    def get_page_size(self, request):
        if self.page_size_query_param in request.query_params:
            return request.query_params.get(self.page_size_query_param)
        return self.page_size