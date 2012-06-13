from django.core.signing import Signer, BadSignature
from services.models import Email, Invite
from datetime import datetime

class FromEmailMiddleware(object):
    def process_request(self, request):
        message_hash = request.GET.get('mh', '')
        if message_hash and len(message_hash)==20:
            for email in Email.objects.filter(hash=message_hash, is_read=False):
                email.mark_read()


class InviteMiddleware(object):
        def process_request(self, request):
            #TODO: invite key add to settings
            token = request.GET.get('inv')
            if token:
                try:
                    Signer().unsign(token)
                except BadSignature:
                    #TODO: Logging, not raise, but hack?
                    raise

                try:
                    action = int(token.split(':', 1)[0])
                except :
                    #TODO: Logging...
                    raise

                invite = Invite.objects.get(pk=action)
                if not invite.view_time:
                    invite.action_time = datetime.now()
                    invite.save()

                if request.user and (not invite.reg_time):
                    invite.reg_time = datetime.now()
                    invite.reg_user = request.user
                    invite.save()
