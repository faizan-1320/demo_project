from celery import shared_task
from project.utils import custom_eamil
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

@shared_task
def celery_mail(to_email=None,context={},template_name=''):
        custom_eamil.send_custom_mail(to_email=to_email,context=context,template_name=template_name)
        return 'Email sent successfully'

@shared_task
def send_contact_email(subject, plain_text_body, html_body, recipient_email):
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
    return 'Email sent successfully'