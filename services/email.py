from datetime import datetime
import hashlib
from urllib import urlencode

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import boto
from boto.ses import SESConnection
from lxml.etree import tostring
from lxml.html.soupparser import fromstring

from grakon.utils import project_settings
from services.models import Email

# TODO: ability to attach files
# TODO: check user's subscription settings? (some emails should be sent anyway)
# TODO: not all tags are allowed in emails (e.g. avoid <p/>) - check and warn
def send_email(recipient, subject, template, ctx, type, from_email='noreply', reply_to=None, to_email=None):
    """ To send emails to admin account set recipient=None """
    # TODO: generate unsubscribe link with hash (page with confirmation); default place for it in base template
    context = project_settings()
    context.update(ctx)
    context['recipient'] = recipient
    html = render_to_string(template, context)

    # TODO: convert html to text
    # TODO: replace <a href="url">text</a> with 'text url', no GA tracking in it
    text = html

    name = str(recipient.user_id) if recipient else 'grakon'
    hash = hashlib.md5(name+' '+str(datetime.now())).hexdigest()[:20]

    params = urlencode({'mh': hash, 'utm_campaign': type, 'utm_medium': 'email', 'utm_source': 'main'})

    xml = fromstring(html)
    for a in xml.findall('.//a'):
        url = a.get('href')
        if url.startswith(settings.URL_PREFIX):
            # If hash is inside url - move it to the end of the newly generated link
            if '#' in url:
                start, end = url.split('#')
                url = start + ('&' if '?' in url else '?') + params + '#' + end
            else:
                url += ('&' if '?' in url else '?') + params

        a.set('href', url)

    img1x1 = xml.find(".//img[@id='img1x1']")
    if img1x1 is not None:
        img1x1.set('src', img1x1.get('src')+'?mh='+hash)

    html = tostring(xml)

    from_str = u'%s <%s>' % settings.EMAILS[from_email]
    if to_email is None:
        to_email = recipient.user.email if recipient else settings.ADMIN_EMAIL
    # TODO: check that email has appropriate format (like no dot at the end)

    headers = {}
    if reply_to:
        headers['Reply-To'] = reply_to

    msg = EmailMultiAlternatives(subject, text, from_str, [to_email], headers=headers)
    msg.attach_alternative(html, "text/html")

    message = msg.message().as_string()

    # TODO: set priority
    email = Email(recipient=recipient, hash=hash, type=type, raw_msg=message, from_email=from_email,
            to_email=to_email, priority=0)
    email.save()

    send_email_task(email) # TODO: run it in celery (use select_related)

# TODO: rename
def send_email_task(email):
    conn = boto.connect_ses(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    try:
        response = conn.send_raw_email(raw_message=email.raw_msg.decode('utf8'),
                destinations=email.to_email,
                source=settings.EMAILS[email.from_email][1])
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
