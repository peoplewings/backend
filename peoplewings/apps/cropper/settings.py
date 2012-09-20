from django.conf import settings

ROOT = getattr(settings, 'CROPPER_ROOT', '').rstrip('/')
MAX_WIDTH  = getattr(settings, 'CROPPER_MAX_WIDTH',  4680)
MAX_HEIGHT = getattr(settings, 'CROPPER_MAX_HEIGHT', 4024)
MIN_WIDTH  = getattr(settings, 'CROPPER_MIN_WIDTH',  256)
MIN_HEIGHT  = getattr(settings, 'CROPPER_MIN_HEIGHT',  320)
ALLOWED_DIMENSIONS = getattr(settings, 'CROPPER_ALLOWED_DIMENSIONS', ())

SHOW_ADMIN = getattr(settings, 'CROPPER_SHOW_ADMIN', True)
