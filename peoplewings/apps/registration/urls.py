"""
Backwards-compatible URLconf for existing django-registration
installs; this allows the standard ``include('registration.urls')`` to
continue working, but that usage is deprecated and will be removed for
django-registration 1.0. For new installs, use
``include('registration.backends.default.urls')``.

"""

import warnings

warnings.warn("include('peoplewings.apps.registration.urls') is deprecated; use include('peoplewings.apps.registration.backends.custom.urls') instead.",
              PendingDeprecationWarning)

from peoplewings.apps.registration.backends.custom.urls import *
