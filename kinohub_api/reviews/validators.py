import datetime

from django.core.exceptions import ValidationError


def year_validator(value):
    """Валидатор проверяющий, что создание произведения произошло в прошлом."""
    if value > datetime.datetime.now().year:
        raise ValidationError('Произведение ещё не появилось.')
