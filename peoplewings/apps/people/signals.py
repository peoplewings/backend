from django.dispatch import Signal

# A user deletes his account
user_deleted = Signal(providing_args=["request"])
profile_created = Signal(providing_args=["profile", "first_name"])