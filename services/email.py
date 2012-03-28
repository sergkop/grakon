from django.conf import settings
from django.core.mail import EmailMultiAlternatives

# TODO: set reply_to
def send_html_email(subject, email, text, html)
    msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html, "text/html")
    msg.send()
