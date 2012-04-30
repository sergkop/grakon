from services.models import Email

class FromEmailMiddleware(object):
    def process_request(self, request):
        message_hash = request.GET.get('mh', '')
        if message_hash and len(message_hash)==20:
            for email in Email.objects.filter(hash=message_hash, is_read=False):
                email.mark_read()
