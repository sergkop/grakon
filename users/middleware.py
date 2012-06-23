class ProfileMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            request.profile = request.user.get_profile()
            request.profile_info = request.profile.info(related=True)
            request.PROFILE = {
                'id': request.profile.id,
                'username': request.profile.username,
                'full_name': unicode(request.profile),
            }
        else:
            request.profile = None
            request.PROFILE = {}
