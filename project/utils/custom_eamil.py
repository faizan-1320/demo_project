# pylint: disable=E0401,W0102,W0718
'''Comman Email send function'''
from django.core.mail import EmailMessage
from django.template import Template, Context
from django.conf import settings
from project.customadmin.models import EmailTemplate

def send_custom_mail(to_email=None, template_name="", context={}):
    """Email Function For Admin"""
    try:
        email_template = EmailTemplate.objects.filter(template_name=template_name).first()
        if not email_template:
            return None, None

        template = Template(email_template.body)
        context = Context(context)
        email_body = template.render(context)

        email = EmailMessage(
            subject=email_template.subject,
            body=email_body,
            from_email=settings.EMAIL_HOST_USER,
            to=[to_email],
        )
        email.content_subtype = "html"

        email.send(fail_silently=False)

        return True

    except EmailTemplate.DoesNotExist:
        return None, None

    except Exception as e:
        print('An error occurred:', e)
        return False
