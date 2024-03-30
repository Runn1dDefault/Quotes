import re

from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class MinWordCountValidator(BaseValidator):
    message = _("Must contain at least %(limit_value)s words.")
    code = "min_length"

    def compare(self, a, b):
        return a < b

    def clean(self, x):
        return len(re.findall(r"\w+", x))

