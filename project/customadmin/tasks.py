from celery import shared_task
from project.utils import custom_eamil

@shared_task
def celery_mail(to_email=None,context={},template_name=''):
        custom_eamil.send_custom_mail(to_email=to_email,context=context,template_name=template_name)
        return 'Email sent successfully'