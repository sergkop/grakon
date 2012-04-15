class ProfileMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            # TODO: get profile info
            request.profile = request.user.get_profile()
        else:
            request.profile = None
