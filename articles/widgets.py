import pytz
from django.conf import settings
from django.forms import MultiWidget, Select
from django.utils.dateparse import parse_datetime
from django.utils.datetime_safe import datetime
from django.utils.timezone import get_current_timezone_name
from wagtail.admin.widgets.datetime import AdminDateTimeInput

TIMEZONE_CHOICES = [
    (zone, zone)
    for zone in getattr(settings, "WAGTAIL_USER_TIME_ZONES", pytz.common_timezones)
]


class AdminTimezoneDateTimeInput(MultiWidget):
    """
    This widget is equivalent in its signatures to AdminDateTimeInput,
    but it allows the user to select the timezone.
    Since the datetime is converted to the database timezone when saved,
    the event timezone name won't be preserved.
    When needed: TODO Add an extra field to preserve the timezone name.
    """

    def __init__(self, attrs=None):
        widgets = [AdminDateTimeInput(), Select(choices=TIMEZONE_CHOICES)]

        super().__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value: datetime):
        """
        The value is given in the user timezone, which can be set by
        the user in their profile.
        """
        current_tz = get_current_timezone_name()
        if value is None:
            return ["", current_tz]
        return [value, current_tz]

    def value_from_datadict(self, data, files, name):
        date, tz = super().value_from_datadict(data, files, name)

        if not date:
            return None

        pytz_tz = pytz.timezone(tz)
        return pytz_tz.localize(parse_datetime(date))
