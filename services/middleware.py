from services.models import Email

class FromEmailMiddleware(object):
    def process_request(self, request):
        message_hash = request.GET.get('mh', '')
        if message_hash: # TODO: also check hash length (extra filter)
            for email in Email.objects.filter(hash=message_hash, is_read=False):
                email.mark_read()
