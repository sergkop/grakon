from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import boto
import dkim

from grakon.utils import project_settings
from services.models import Email

# TODO: ability to attach files
# TODO: check user's subscription settings?
def send_email(recipient, subject, template, ctx, type, from_email, reply_to=None):
    # TODO: generate unsubscribe link with hash (page with confirmation); default place for it in base template

    context = project_settings()
    context.update(ctx)
    html = render_to_string(template, context)

    # TODO: convert html to text, replace links by 'title (url)', no GA tracking in it
    text = html

    # TODO: add GA tracking parameters to urls, starting with http://grakon.org (bool to turn it on).
    #       Do it automatically by parsing html; use campaigns and url id inside messages
    # TODO: minify html before sending
    # TODO: add hash to links at grakon.org
    # TODO: append 1x1 px image to track opening

    # TODO: set reply_to
    from_str = u'%s <%s>' % settings.EMAILS[from_email]
    msg = EmailMultiAlternatives(subject, text, from_str, [recipient.user.email])
    msg.attach_alternative(html, "text/html")
    #msg.send()

    """
    To enable DKIM signing you should specify values for the DKIM_PRIVATE_KEY and DKIM_DOMAIN settings.
    You can generate a private key with a command such as openssl genrsa 512 and get the public key portion
    with openssl rsa -pubout <private.key. The public key should be published to ses._domainkey.example.com
    if your domain is example.com. You can use a different name instead of ses by changing the DKIM_SELECTOR setting.
    """
    message = msg.message().as_string()

    # Sign headers with DKIM
    # TODO: test it
    #sig = dkim.sign(message, settings.DKIM_SELECTOR, settings.DKIM_DOMAIN, settings.DKIM_PRIVATE_KEY,
    #        include_headers=['From', 'To', 'Cc', 'Subject', 'Reply-To'])
    #message = sig + message

    hash = 'erger' # TODO: hash is a function of recipient id and timestamp
    # TODO: set priority
    email = Email(recipient=recipient, hash=hash, type=type, raw_msg=message, from_email=from_email,
            read_time=datetime.now(), priority=0)
    email.save()

    send_email_task(email) # TODO: run it in celery (use select_related)

# TODO: rename
def send_email_task(email):
    conn = boto.connect_ses(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    try:
        # TODO: specify source
        # TODO: use select_related
        response = conn.send_raw_email(destinations=email.recipient.user.email,
                raw_message=email.raw_msg)
    except SESConnection.ResponseError, err:
        error_keys = ['status', 'reason', 'body', 'request_id',
                        'error_code', 'error_message']
        for key in error_keys:
            print key, getattr(err, key, None)
        # TODO: update_status
        # TODO: what if message is rejected? parse error message
        # TODO: catch different errors and process differently (postpone or cancel)
    else:
        email.update_status('sent')

    # TODO: save message id?
    #response['SendRawEmailResponse']['SendRawEmailResult']['MessageId']
    #response['SendRawEmailResponse']['ResponseMetadata']['RequestId']

# TODO: task which retrives bounce and spam report mails, extracts data, updates Email and unsubscribes user
