class ProfileMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            request.profile = request.user.get_profile()
            request.profile_info = request.profile.info(related=True)
            request.PROFILE = {
                'id': request.profile.id,
                'full_name': unicode(request.profile),
                'url': request.profile.get_absolute_url(),
            }

            # used for Google Analytics custom variable
            request.user_type = 'active' if request.profile.rating>1 else 'logged in'
        else:
            request.profile = None
            request.PROFILE = {}
            request.user_type = 'anonym'
