"""
This module contains Celery tasks for sending emails, including 
custom emails and contact emails.
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from celery import shared_task
from project.utils import custom_eamil # pylint: disable=E0401

@shared_task
def celery_mail(to_email=None, context=None, template_name=''):
    """
    Sends an email using a custom email function.

    Args:
        to_email (str): The recipient's email address.
        context (dict): The context for the email template.
        template_name (str): The name of the email template.

    Returns:
        str: Confirmation message.
    """
    if context is None:
        context = {}
    custom_eamil.send_custom_mail(to_email=to_email, context=context, template_name=template_name)
    return 'Email sent successfully'

@shared_task
def send_contact_email(subject, plain_text_body, html_body, recipient_email):
    """
    Sends a contact email with both plain text and HTML versions.

    Args:
        subject (str): The subject of the email.
        plain_text_body (str): The plain text version of the email body.
        html_body (str): The HTML version of the email body.
        recipient_email (str): The recipient's email address.

    Returns:
        str: Confirmation message.
    """
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text_body,
        from_email=settings.EMAIL_HOST_USER,
        to=[recipient_email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
    return 'Email sent successfully'
