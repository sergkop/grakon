from django.conf import settings

def disqus_page_params(identifier, url, category):
    return {
        'disqus_identifier': identifier,
        'disqus_url': settings.DISQUS_URL_PREFIX+url,
        'disqus_category_id': settings.DISQUS_CATEGORIES[category],
        'disqus_partial_url': url,
    }
