import logging
import threading
import time

local = threading.local()

class LogUserContextMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        setattr(local, 'user', request.user.username)
        setattr(local, 'response_time', response_time)
        setattr(local, 'ip', ip)
        setattr(local, 'request_path', request.path)

        return response

class UserContextFilter(logging.Filter):
    def filter(self, record):

        user = getattr(local, 'user', None)
        if user:
            record.username = user
        else:
            record.username = 'AnonymousUser'

        response_time = getattr(local, 'response_time', None)
        if response_time:
            record.response_time = response_time
        else:
            record.response_time = 0

        ip = getattr(local, 'ip', None)
        if ip:
            record.ip = ip
        else:
            record.ip = '0.0.0.0'

        return True

class SessionCheckFilter(logging.Filter):
    def filter(self, record):
        request_path = getattr(local, 'request_path', '')
        if request_path == '/session/duplicatelogincheck':
            return False
        else:
            return True

class NoTracebackFilter(logging.Filter):
    def filter(self, record):
        return not record.exc_info
