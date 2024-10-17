"""
This module contains Celery tasks for sending emails, including 
custom emails and contact emails.
"""

from datetime import timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from celery import shared_task
from django.utils import timezone
from project.utils import custom_eamil # pylint: disable=E0401
from project.order.models import Order
from project.users.models import Wishlist

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

@shared_task
def send_daily_orders_report():
    # Get the current time and the time 24 hours ago
    now = timezone.now()
    yesterday = now - timedelta(days=1)

    # Query for orders placed within the last 24 hours
    orders = Order.objects.filter(created_at__gte=yesterday)

    if orders.exists():
        # Prepare email content
        email_body = """
        <h2 style="font-family: Arial, sans-serif; color: #333;">Daily Orders Report</h2>
        <p style="font-family: Arial, sans-serif; color: #555;">Here are the orders placed within the last 24 hours:</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left; color: #333;">Order ID</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left; color: #333;">Customer Email</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left; color: #333;">Total Amount</th>
                </tr>
            </thead>
            <tbody>
        """

        for order in orders:
            email_body += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #333;">{order.order_id}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #333;">{order.user.email}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #333;">${order.total_amount:.2f}</td>
                </tr>
            """

        email_body += """
            </tbody>
        </table>
        <p style="font-family: Arial, sans-serif; color: #555; margin-top: 20px;">Best regards,<br>Your E-Shopper Support Team</p>
        """

        # Prepare the email
        subject = "Daily Orders Report"
        from_email = "faizanmahammed.neosoftmail@gmail.com"
        to_email = "faizanmahammed.neosoftmail@gmail.com"

        email = EmailMultiAlternatives(subject, "", from_email, [to_email])
        email.attach_alternative(email_body, "text/html")

        # Send the email
        email.send()
        print('Successfully sent daily orders report to admin')
    else:
        print('No orders were placed in the last 24 hours.')

@shared_task
def send_weekly_wishlist_report():
    # Get the current time and the time a week ago
    now = timezone.now()
    week_ago = now - timedelta(weeks=1)

    # Query for active wish list items (that are not deleted) added in the last week
    wishlists = Wishlist.objects.filter(is_active=True, is_delete=False)

    if wishlists.exists():
        # Prepare email content
        email_body = """
        <h2 style="font-family: Arial, sans-serif; color: #333;">Weekly Wishlist Report</h2>
        <p style="font-family: Arial, sans-serif; color: #555;">Here are the wish list items:</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
            <thead>
                <tr style="background-color: #f2f2f2;">
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left; color: #333;">User Email</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left; color: #333;">Product Name</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left; color: #333;">Product ID</th>
                    <th style="padding: 10px; border: 1px solid #ddd; text-align: left; color: #333;">Date Added</th>
                </tr>
            </thead>
            <tbody>
        """

        for wishlist in wishlists:
            email_body += f"""
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #333;">{wishlist.user.email}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #333;">{wishlist.product.name}</td> <!-- Assuming the Product model has a name field -->
                    <td style="padding: 10px; border: 1px solid #ddd; color: #333;">{wishlist.product.id}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; color: #333;">{wishlist.created_at.strftime('%Y-%m-%d')}</td> <!-- Assuming you have a created_at field -->
                </tr>
            """

        email_body += """
            </tbody>
        </table>
        <p style="font-family: Arial, sans-serif; color: #555; margin-top: 20px;">Best regards,<br>Your E-Shopper Support Team</p>
        """

        # Prepare the email
        subject = "Weekly Wishlist Report"
        from_email = "faizanmahammed.neosoftmail@gmail.com"
        to_email = "faizanmahammed.neosoftmail@gmail.com"

        email = EmailMultiAlternatives(subject, "", from_email, [to_email])
        email.attach_alternative(email_body, "text/html")

        # Send the email
        email.send()
        print('Successfully sent weekly wishlist report to admin')
    else:
        print('No active wish list items found.')