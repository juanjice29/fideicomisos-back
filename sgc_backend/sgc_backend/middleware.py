from threading import local
import uuid
from django.utils.deprecation import MiddlewareMixin
_thread_locals = local()

def get_current_request():
    return getattr(_thread_locals, 'request', None)

class CurrentRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        return self.get_response(request)

class RequestIdMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _thread_locals.value = uuid.uuid4()

def get_request_id():
    return getattr(_thread_locals, 'value', None)

