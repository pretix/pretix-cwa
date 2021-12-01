import cwa_qr
import hashlib
from datetime import timedelta
from django.conf import settings
from pretix.base.models import Event, SubEvent
from pytz import UTC


def clean_address(a):
    a = a.replace("\r\n", ", ")
    a = a.replace("\r", ", ")
    a = a.replace("\n", ", ")
    return a


def generate_url(event: Event, subevent: SubEvent = None):
    ev = subevent or event
    event_description = cwa_qr.CwaEventDescription()
    event_description.location_description = str(ev.name)[:100]
    event_description.location_address = clean_address(
        str(ev.location) or str(event.location) or str(event.name) or ""
    )[:100]
    event_description.location_type = int(ev.settings.cwa_location_type)

    default_length = ev.settings.cwa_default_length

    if event.settings.cwa_mode == "daily":
        start_of_day = ev.date_from.astimezone(event.timezone).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_of_day = ev.date_from.astimezone(event.timezone).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

        if event.has_subevents:
            subevents_today = list(
                event.subevents.filter(
                    date_from__gte=start_of_day, date_from__lte=start_of_day
                )
                .order_by("date_from")
                .values("date_from", "date_admission", "date_to")
            )
            if subevents_today:
                first_subevent = subevents_today[0]
                last_subevent = subevents_today[-1]

                lengths = []
                for i, se in enumerate(subevents_today):
                    if se["date_to"]:
                        lengths.append(se["date_to"] - se["date_from"])
                    elif i != 0:
                        lengths.append(
                            se["date_from"] - subevents_today[i - 1]["date_from"]
                        )
                if lengths:
                    length = sum(lengths, timedelta(hours=0)) / len(lengths)
                else:
                    length = timedelta(hours=4)

                date_from = (
                    first_subevent["date_admission"] or first_subevent["date_from"]
                )
                date_to = last_subevent["date_to"] or (
                    last_subevent["date_from"] + length
                )
                if default_length is None:
                    default_length = length.seconds // 60
            else:
                date_from = start_of_day
                date_to = end_of_day
        else:
            date_from = start_of_day
            date_to = end_of_day
            if default_length is None and ev.date_to:
                default_length = (ev.date_to - ev.date_from).seconds // 60
    else:
        date_from = ev.date_admission or ev.date_from
        date_to = ev.date_to or (date_from + timedelta(hours=4))
        if default_length is None:
            default_length = (date_to - date_from).seconds // 60

    if default_length is None:
        default_length = 4 * 60  # no idea how long events are, fall back to 4h

    event_description.seed = hashlib.sha256(
        ":".join(
            [
                settings.SECRET_KEY,
                "pretix_cwa",
                "seed",
                str(event.pk),
                date_from.isoformat(),
            ]
        ).encode()
    ).digest()[:16]
    event_description.start_date_time = date_from.astimezone(UTC)
    event_description.end_date_time = date_to.astimezone(UTC)
    event_description.default_check_in_length_in_minutes = default_length
    return cwa_qr.generate_url(event_description), date_from, date_to
