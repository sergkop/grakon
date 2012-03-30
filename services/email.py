from django.conf import settings
from django.core.mail import EmailMultiAlternatives

# TODO: add GA tracking parameters to urls, starting with http://grakon.org (bool to turn it on)
# TODO: set reply_to
# TODO: ability to attach files
def send_email(subject, email, html):
    # TODO: convert html to text, replace links by 'title (url)', no GA tracking in it
    text = html

    msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [email])
    msg.attach_alternative(html, "text/html")
    msg.send()
