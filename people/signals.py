from registration.signals import user_activated

user_activated.connect(createUserProfile)

def createUserProfile(sender, user, request, **kwargs):
    UserProfile.objects.create(user=user)