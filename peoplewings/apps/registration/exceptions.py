from django.http import HttpResponse

class ActivationCompleted(Exception):
    def render(self, request):
        return HttpResponse() 

class NotAKey(Exception):
    def render(self, request):
        return HttpResponse() 

class KeyExpired(Exception):
    def render(self, request):
        return HttpResponse()

class NotActive(Exception):
    def render(self, request):
        return HttpResponse()

class AuthFail(Exception):
    def render(self, request):
        return HttpResponse()
