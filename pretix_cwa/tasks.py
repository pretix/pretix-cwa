import logging
from pretix.base.email import get_email_context
from pretix.base.i18n import language
from pretix.base.models import OrderPosition
from pretix.base.services.mail import SendMailException
from pretix.base.services.tasks import EventTask
from pretix.celery_app import app

logger = logging.getLogger(__name__)


@app.task(base=EventTask, bind=True)
def send_email(self, event, position):
    op = OrderPosition.objects.get(pk=position)
    with language(op.order.locale, event.settings.region):
        email_template = event.settings.cwa_checkin_email_body
        email_subject = str(event.settings.cwa_checkin_email_subject)

        email_context = get_email_context(event=event, order=op.order, position=op)
        try:
            if op.attendee_email:
                op.send_mail(
                    email_subject,
                    email_template,
                    email_context,
                    "pretix_cwa.order.position.email.cwa",
                )
            else:
                op.order.send_mail(
                    email_subject,
                    email_template,
                    email_context,
                    "pretix_cwa.order.email.cwa",
                )
        except SendMailException:
            logger.exception("CWA reminder email could not be sent")
