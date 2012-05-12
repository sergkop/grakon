import base64
import json
import hashlib
import hmac
import time

from django.conf import settings

def disqus_sso_message(profile):
    """ Take user profile or None """
    if profile:
        data = json.dumps({
            'id': profile.username+str(profile.id),
            'username': unicode(profile),
            'email': profile.user.email,
            'url': settings.URL_PREFIX+profile.get_absolute_url(),
            # TODO: avatar
        })
    else:
        data = '{}'

    message = base64.b64encode(data)
    timestamp = int(time.time())
    sig = hmac.HMAC(settings.DISQUS_SECRET_KEY, '%s %s' % (message, timestamp), hashlib.sha1).hexdigest()
    return message + ' ' + sig + ' ' + str(timestamp)

def disqus_page_params(identifier, url, category):
    return {
        'disqus_identifier': identifier,
        'disqus_url': settings.DISQUS_URL_PREFIX+url,
        'disqus_category_id': settings.DISQUS_CATEGORIES[category],
        'disqus_partial_url': url,
    }
