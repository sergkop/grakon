from django.shortcuts import redirect

def authenticated_profile_redirect(view):
    """ Decorator for views which need to redirect to the profile page if user is authenticated """
    def new_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(request.profile.get_absolute_url())
        return view(request, *args, **kwargs)

    return new_view
