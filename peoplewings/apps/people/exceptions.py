from django.http import HttpResponse

class FriendYourselfError(Exception):
    def render(self, request):
        return HttpResponse()

class CannotAcceptOrRejectError(Exception):
    def render(self, request):
        return HttpResponse()

class InvalidAcceptRejectError(Exception):
    def render(self, request):
        return HttpResponse()