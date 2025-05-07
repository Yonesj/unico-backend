from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class FileSizeValidator:
    """
    Validator for file size that can be applied on any FileField/ImageField.
    """
    message = _("File size must be under %(max_mb)d MB. Current file is %(current_mb).1f MB.")
    code    = 'file_too_large'

    def __init__(self, max_mb=4):
        self.max_mb = max_mb
        self.max_bytes = max_mb * 1024 * 1024

    def __call__(self, file):
        size = getattr(file, 'size', None)

        if size is None:
            return

        if int(size) > self.max_bytes:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    'max_mb': self.max_mb,
                    'current_mb': size / (1024 * 1024)
                }
            )
