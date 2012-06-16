class ProfileMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            request.profile = request.user.get_profile()
            request.profile_info = request.profile.info(related=False)
        else:
            request.profile = None
