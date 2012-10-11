from django.http import HttpResponse

class BadParameters(Exception):
    def render(self, request):
        return HttpResponse()

class NotAUser(Exception):
    def render(self, request):
        return HttpResponse()

